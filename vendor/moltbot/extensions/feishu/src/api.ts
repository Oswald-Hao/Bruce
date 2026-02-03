import crypto from "node:crypto";
import type {
  FeishuSendMessageRequest,
  FeishuSendMessageResponse,
  FeishuUserInfo,
  FeishuChatInfo,
  FeishuMediaUploadResponse,
} from "./types.js";
import type { ResolvedFeishuAccount } from "./types.config.js";

// Feishu API base URLs
const FEISHU_API_BASE = "https://open.feishu.cn/open-apis";
const LARK_API_BASE = "https://open.larksuite.com/open-apis";

// Token cache (in production, this should use proper cache with expiration)
const tokenCache = new Map<string, { token: string; expireAt: number }>();

/**
 * Get API base URL based on app type
 */
export const getApiBaseUrl = (appType?: string): string => {
  // Default to Feishu (Chinese version)
  return FEISHU_API_BASE;
};

/**
 * Get tenant access token for API calls
 */
export const getTenantAccessToken = async (
  account: ResolvedFeishuAccount
): Promise<string> => {
  const cacheKey = account.accountId;

  // Check cache first
  const cached = tokenCache.get(cacheKey);
  if (cached && cached.expireAt > Date.now()) {
    return cached.token;
  }

  // Request new token
  const requestBody = {
    app_id: account.config.appId,
    app_secret: account.config.appSecret,
  };
  console.log(`[feishu] [API] Getting tenant access token for account: ${account.accountId}`);
  console.log(`[feishu] [API] Request body app_id: ${requestBody.app_id}`);
  console.log(`[feishu] [API] Request URL: ${getApiBaseUrl(account.config.appType)}/auth/v3/tenant_access_token/internal`);

  const response = await fetch(`${getApiBaseUrl(account.config.appType)}/auth/v3/tenant_access_token/internal`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    console.error(`[feishu] [API] Response not OK: ${response.status} ${response.statusText}`);
    throw new Error(`Failed to get tenant access token: ${response.statusText}`);
  }

  const data: { code?: number; tenant_access_token?: string; expire?: number } = await response.json();
  console.log(`[feishu] [API] Response code: ${data.code}`);

  if (data.code !== 0 || !data.tenant_access_token) {
    console.error(`[feishu] [API] Failed to get token. Response:`, JSON.stringify(data));
    throw new Error(`Failed to get tenant access token: ${JSON.stringify(data)}`);
  }

  console.log(`[feishu] [API] Successfully got tenant access token, expires in ${data.expire}s`);

  // Cache token (expire 5 minutes before actual expiration)
  const expireAt = Date.now() + (data.expire || 7200) * 1000 - 300000;
  tokenCache.set(cacheKey, { token: data.tenant_access_token, expireAt });

  return data.tenant_access_token;
};

/**
 * Upload image to Feishu and get image_key
 */
export const uploadFeishuImage = async ({
  account,
  imageBuffer,
  imageType = "message",
}: {
  account: ResolvedFeishuAccount;
  imageBuffer: Buffer | Uint8Array;
  imageType?: "message" | "avatar";
}): Promise<string> => {
  const token = await getTenantAccessToken(account);

  const formData = new FormData();
  formData.append("image_type", imageType);
  formData.append("image", new Blob([imageBuffer]), "screenshot.png");

  console.log(`[feishu] [API] Uploading image...`);
  console.log(`[feishu] [API]   image_type: ${imageType}`);
  console.log(`[feishu] [API]   size: ${imageBuffer.length} bytes`);

  const response = await fetch(`${getApiBaseUrl(account.config.appType)}/im/v1/images`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Failed to upload image: ${response.statusText}`);
  }

  const data: {
    code: number;
    msg?: string;
    data?: {
      image_key: string;
    };
  } = await response.json();

  if (data.code !== 0 || !data.data?.image_key) {
    console.error(`[feishu] [API] Upload image failed:`, data);
    throw new Error(`Failed to upload image: ${data.msg} (code: ${data.code})`);
  }

  console.log(`[feishu] [API] ✓ Image uploaded successfully! image_key: ${data.data.image_key}`);
  return data.data.image_key;
};

/**
 * Send message to Feishu (supports text, image, etc.)
 */
export const sendFeishuMessage = async ({
  account,
  receiveId,
  receiveIdType = "open_id",
  msgType = "text",
  content,
  parentId,
}: {
  account: ResolvedFeishuAccount;
  receiveId: string;
  receiveIdType?: "open_id" | "user_id" | "union_id" | "chat_id";
  msgType?: "text" | "post" | "image" | "file" | "audio" | "video" | "media" | "interactive";
  content: string | Record<string, unknown>;
  parentId?: string;
}): Promise<FeishuSendMessageResponse> => {
  const token = await getTenantAccessToken(account);

  // Build content object first
  let contentObj: Record<string, unknown>;
  if (typeof content === "string") {
    try {
      contentObj = JSON.parse(content);
    } catch {
      // If parsing fails, treat as plain text
      contentObj = { text: content };
    }
  } else {
    contentObj = content;
  }

  // IMPORTANT: Working format discovered through testing:
  // 1. receive_id_type in URL query params
  // 2. receive_id AND open_id/chat_id field BOTH in body
  // 3. msg_type in body
  // 4. content as an OBJECT (not JSON string!)
  // 5. parent_id for reply threading (optional)
  const requestBody: Record<string, unknown> = {
    receive_id: receiveId,
    [receiveIdType]: receiveId,  // Add explicit open_id or chat_id field
    msg_type: msgType,
    content: contentObj,  // Use object directly, not JSON string!
    uuid: crypto.randomUUID(),
  };

  // Add parent_id if provided (for reply threading)
  if (parentId) {
    requestBody.parent_id = parentId;
  }

  console.log(`[feishu] [API] Sending message:`);
  console.log(`[feishu] [API]   receive_id: ${receiveId}`);
  console.log(`[feishu] [API]   receive_id_type: ${receiveIdType} (URL param)`);
  console.log(`[feishu] [API]   msg_type: ${msgType}`);
  console.log(`[feishu] [API]   content (object):`, JSON.stringify(contentObj).substring(0, 100));
  console.log(`[feishu] [API]   Full request body:`, JSON.stringify(requestBody));

  const response = await fetch(`${getApiBaseUrl(account.config.appType)}/message/v4/send?receive_id_type=${receiveIdType}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Authorization": `Bearer ${token}`,
      // Add custom app header (from user's successful test)
      "X-Custom-Auth": "t-g1041tjP63RE55E7GSZH6CRXVRNRO7VPUKKZX6JU",
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    throw new Error(`Failed to send message: ${response.statusText}`);
  }

  const data: FeishuSendMessageResponse = await response.json();

  console.log(`[feishu] [API] Send message response:`, JSON.stringify(data, null, 2));

  if (data.code !== 0) {
    console.error(`[feishu] [API] Send message failed. Response:`, JSON.stringify(data));
    throw new Error(`Failed to send message: ${data.msg} (code: ${data.code})`);
  }

  // Fix: API returns data.message_id, not data.data.msg_id
  const messageId = (data as any).message_id || data.data?.msg_id;
  console.log(`[feishu] [API] ✓ Message sent successfully! Message ID: ${messageId}`);
  return data;
};

/**
 * Upload media file to Feishu
 */
export const uploadFeishuMedia = async ({
  account,
  file,
  fileType,
  parentType = "chat",
}: {
  account: ResolvedFeishuAccount;
  file: Buffer | Uint8Array;
  fileType: "image" | "file" | "video" | "audio";
  parentType?: "chat" | "email";
}): Promise<string> => {
  const token = await getTenantAccessToken(account);

  const formData = new FormData();
  formData.append("file_type", fileType);
  formData.append("parent_type", parentType);
  formData.append("file", new Blob([file]), "upload");

  const response = await fetch(`${getApiBaseUrl(account.config.appType)}/drive/v1/medias/upload_all`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Failed to upload media: ${response.statusText}`);
  }

  const data: FeishuMediaUploadResponse = await response.json();

  if (data.code !== 0 || !data.data?.file_key) {
    throw new Error(`Failed to upload media: ${data.msg} (code: ${data.code})`);
  }

  return data.data.file_key;
};

/**
 * Get user info by user_id or open_id
 */
export const getFeishuUserInfo = async ({
  account,
  userId,
  userIdType = "open_id",
}: {
  account: ResolvedFeishuAccount;
  userId: string;
  userIdType?: "open_id" | "user_id" | "union_id";
}): Promise<FeishuUserInfo> => {
  const token = await getTenantAccessToken(account);

  const response = await fetch(
    `${getApiBaseUrl(account.config.appType)}/contact/v3/users/${userId}?user_id_type=${userIdType}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to get user info: ${response.statusText}`);
  }

  const data: { code?: number; data?: FeishuUserInfo } = await response.json();

  if (data.code !== 0 || !data.data) {
    throw new Error(`Failed to get user info: code ${data.code}`);
  }

  return data.data;
};

/**
 * Get chat info by chat_id
 */
export const getFeishuChatInfo = async ({
  account,
  chatId,
}: {
  account: ResolvedFeishuAccount;
  chatId: string;
}): Promise<FeishuChatInfo> => {
  const token = await getTenantAccessToken(account);

  const response = await fetch(
    `${getApiBaseUrl(account.config.appType)}/im/v1/chats/${chatId}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to get chat info: ${response.statusText}`);
  }

  const data: { code?: number; data?: FeishuChatInfo } = await response.json();

  if (data.code !== 0 || !data.data) {
    throw new Error(`Failed to get chat info: code ${data.code}`);
  }

  return data.data;
};

/**
 * Update message in Feishu
 */
export const updateFeishuMessage = async ({
  account,
  messageId,
  msgType = "text",
  content,
}: {
  account: ResolvedFeishuAccount;
  messageId: string;
  msgType?: "text" | "post" | "interactive";
  content: string | Record<string, unknown>;
}): Promise<void> => {
  const token = await getTenantAccessToken(account);

  // Build content object
  let contentObj: Record<string, unknown>;
  if (typeof content === "string") {
    try {
      contentObj = JSON.parse(content);
    } catch {
      contentObj = { text: content };
    }
  } else {
    contentObj = content;
  }

  const requestBody = {
    msg_type: msgType,
    content: contentObj,
  };

  console.log(`[feishu] [API] Updating message: ${messageId}`);
  console.log(`[feishu] [API]   msg_type: ${msgType}`);
  console.log(`[feishu] [API]   content:`, JSON.stringify(contentObj).substring(0, 100));

  const response = await fetch(`${getApiBaseUrl(account.config.appType)}/im/v1/messages/${messageId}/update`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    throw new Error(`Failed to update message: ${response.statusText}`);
  }

  const data = await response.json();

  if (data.code !== 0) {
    console.error(`[feishu] [API] Update message failed. Response:`, JSON.stringify(data));
    throw new Error(`Failed to update message: ${data.msg} (code: ${data.code})`);
  }

  console.log(`[feishu] [API] ✓ Message updated successfully!`);
};

/**
 * Verify webhook signature
 */
export const verifyFeishuWebhook = ({
  signature,
  timestamp,
  nonce,
  body,
  encryptKey,
}: {
  signature: string;
  timestamp: string;
  nonce: string;
  body: string;
  encryptKey: string;
}): boolean => {
  // Concatenate timestamp, nonce, and body
  const content = `${timestamp}${nonce}${body}`;

  // Compute SHA256 signature
  const computedSignature = crypto
    .createHmac("sha256", encryptKey)
    .update(content)
    .digest("base64");

  // Compare signatures
  return signature === computedSignature;
};

/**
 * Add typing indicator (via emoji reaction) to a message
 * Uses Feishu's special "Typing" emoji to show "typing" status
 * @see https://open.feishu.cn/document/server-docs/im-v1/message-reaction/create
 */
export const addTypingIndicator = async ({
  account,
  messageId,
}: {
  account: ResolvedFeishuAccount;
  messageId: string;
}): Promise<string | null> => {
  const token = await getTenantAccessToken(account);

  // Feishu emoji for typing indicator
  // Note: "Typing" emoji may not exist, using common emojis instead
  // Try different emojis: "THINKING", "WAVE", "SMILE"
  const requestBody = {
    reaction_type: {
      emoji_type: "THINKING",  // Use THINKING emoji instead of Typing
    },
  };

  console.log(`[feishu] [API] Adding typing indicator to message: ${messageId}`);

  const response = await fetch(
    `${getApiBaseUrl(account.config.appType)}/im/v1/messages/${messageId}/reactions`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify(requestBody),
    }
  );

  if (!response.ok) {
    const errorText = await response.text();
    console.error(`[feishu] [API] Failed to add typing indicator: ${response.status} ${response.statusText}`);
    console.error(`[feishu] [API] Error response:`, errorText);
    return null;
  }

  const data: {
    code: number;
    msg?: string;
    data?: {
      reaction_id: string;
    };
  } = await response.json();

  if (data.code !== 0 || !data.data?.reaction_id) {
    console.error(`[feishu] [API] Add typing indicator failed:`, data);
    return null;
  }

  console.log(`[feishu] [API] ✓ Typing indicator added! reaction_id: ${data.data.reaction_id}`);
  return data.data.reaction_id;
};

/**
 * Remove a reaction from a message (used to remove typing indicator)
 * @see https://open.feishu.cn/document/server-docs/im-v1/message-reaction/delete
 */
export const removeReaction = async ({
  account,
  messageId,
  reactionId,
}: {
  account: ResolvedFeishuAccount;
  messageId: string;
  reactionId: string;
}): Promise<boolean> => {
  const token = await getTenantAccessToken(account);

  console.log(`[feishu] [API] Removing reaction: ${reactionId} from message: ${messageId}`);

  const response = await fetch(
    `${getApiBaseUrl(account.config.appType)}/im/v1/messages/${messageId}/reactions/${reactionId}`,
    {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    console.error(`[feishu] [API] Failed to remove reaction: ${response.statusText}`);
    return false;
  }

  const data: { code: number; msg?: string } = await response.json();

  if (data.code !== 0) {
    console.error(`[feishu] [API] Remove reaction failed:`, data);
    return false;
  }

  console.log(`[feishu] [API] ✓ Reaction removed successfully!`);
  return true;
};

/**
 * Probe Feishu connection (health check)
 */
export const probeFeishu = async ({
  account,
}: {
  account: ResolvedFeishuAccount;
}): Promise<boolean> => {
  try {
    // Try to get tenant access token
    await getTenantAccessToken(account);
    return true;
  } catch (error) {
    console.error("Feishu probe failed:", error);
    return false;
  }
};
// Test auto-sync at 2026年 02月 03日 星期二 11:16:52 CST
// Test auto-sync at 2026年 02月 03日 星期二 13:47:47 CST
