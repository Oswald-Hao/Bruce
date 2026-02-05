/**
 * Feishu Streaming Card Support
 *
 * Implements typing indicator and streaming text output for Feishu using
 * the Card Kit streaming API.
 *
 * Flow:
 * 1. Create a card entity with streaming_mode: true
 * 2. Send the card as a message (shows "[Generating...]" in chat preview)
 * 3. Stream text updates to the card using the cardkit API
 * 4. Close streaming mode when done
 */

import type { ResolvedFeishuAccount } from "./types.config.js";

const FEISHU_API_BASE = "https://open.feishu.cn/open-apis";
const LARK_API_BASE = "https://open.larksuite.com/open-apis";

export type FeishuStreamingCredentials = {
  appId: string;
  appSecret: string;
  appType?: string;
};

export type FeishuStreamingCardState = {
  cardId: string;
  messageId: string;
  sequence: number;
  elementId: string;
  currentText: string;
};

// Token cache
const tokenCache = new Map<string, { token: string; expireAt: number }>();

const getTokenCacheKey = (credentials: FeishuStreamingCredentials) =>
  `${credentials.appId}`;

/**
 * Get API base URL based on app type
 */
const getApiBaseUrl = (appType?: string): string => {
  return FEISHU_API_BASE;
};

/**
 * Get tenant access token (with caching)
 */
async function getTenantAccessToken(credentials: FeishuStreamingCredentials): Promise<string> {
  const cacheKey = getTokenCacheKey(credentials);
  const cached = tokenCache.get(cacheKey);
  if (cached && cached.expireAt > Date.now() + 60000) {
    return cached.token;
  }

  const apiBase = getApiBaseUrl(credentials.appType);
  const response = await fetch(`${apiBase}/auth/v3/tenant_access_token/internal`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      app_id: credentials.appId,
      app_secret: credentials.appSecret,
    }),
  });

  const result = (await response.json()) as {
    code: number;
    msg: string;
    tenant_access_token?: string;
    expire?: number;
  };

  if (result.code !== 0 || !result.tenant_access_token) {
    throw new Error(`Failed to get tenant access token: ${result.msg}`);
  }

  // Cache token (expire 2 hours, we refresh 1 minute early)
  tokenCache.set(cacheKey, {
    token: result.tenant_access_token,
    expiresAt: Date.now() + (result.expire ?? 7200) * 1000,
  });

  return result.tenant_access_token;
}

/**
 * Create a streaming card entity
 */
export async function createStreamingCard(
  credentials: FeishuStreamingCredentials,
  title?: string,
): Promise<{ cardId: string }> {
  const cardJson = {
    schema: "2.0",
    ...(title
      ? {
          header: {
            title: {
              content: title,
              tag: "plain_text",
            },
          },
        }
      : {}),
    config: {
      streaming_mode: true,
      summary: {
        content: "[Generating...]",
      },
      streaming_config: {
        print_frequency_ms: { default: 50 },
        print_step: { default: 2 },
        print_strategy: "fast",
      },
    },
    body: {
      elements: [
        {
          tag: "markdown",
          content: "⏳ Thinking...",
          element_id: "streaming_content",
        },
      ],
    },
  };

  const apiBase = getApiBaseUrl(credentials.appType);
  const response = await fetch(`${apiBase}/cardkit/v1/cards`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${await getTenantAccessToken(credentials)}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type: "card_json",
      data: JSON.stringify(cardJson),
    }),
  });

  const result = (await response.json()) as {
    code: number;
    msg: string;
    data?: { card_id: string };
  };

  if (result.code !== 0 || !result.data?.card_id) {
    throw new Error(`Failed to create streaming card: ${result.msg}`);
  }

  console.log(`[feishu] [STREAMING] Created streaming card: ${result.data.card_id}`);
  return { cardId: result.data.card_id };
}

/**
 * Send a streaming card as a message
 */
export async function sendStreamingCard(
  account: ResolvedFeishuAccount,
  receiveId: string,
  cardId: string,
  receiveIdType: "open_id" | "user_id" | "union_id" | "email" | "chat_id" = "chat_id",
): Promise<{ messageId: string }> {
  const token = await getTenantAccessToken({
    appId: account.config.appId,
    appSecret: account.config.appSecret,
    appType: account.config.appType,
  });

  const content = JSON.stringify({
    type: "card",
    data: { card_id: cardId },
  });

  const apiBase = getApiBaseUrl(account.config.appType);
  const response = await fetch(`${apiBase}/im/v1/messages?receive_id_type=${receiveIdType}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      receive_id: receiveId,
      msg_type: "interactive",
      content,
    }),
  });

  const result = (await response.json()) as {
    code: number;
    msg: string;
    data?: { message_id: string };
  };

  if (result.code !== 0 || !result.data?.message_id) {
    throw new Error(`Failed to send streaming card: ${result.msg}`);
  }

  console.log(`[feishu] [STREAMING] Sent streaming card message: ${result.data.message_id}`);
  return { messageId: result.data.message_id };
}

/**
 * Update streaming card text content
 */
export async function updateStreamingCardText(
  credentials: FeishuStreamingCredentials,
  cardId: string,
  elementId: string,
  text: string,
  sequence: number,
): Promise<void> {
  const apiBase = getApiBaseUrl(credentials.appType);
  const response = await fetch(
    `${apiBase}/cardkit/v1/cards/${cardId}/elements/${elementId}/content`,
    {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${await getTenantAccessToken(credentials)}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        content: text,
        sequence,
        uuid: `stream_${cardId}_${sequence}`,
      }),
    },
  );

  const result = (await response.json()) as { code: number; msg: string };

  if (result.code !== 0) {
    console.warn(`[feishu] [STREAMING] Failed to update streaming card text: ${result.msg}`);
    // Don't throw - streaming updates can fail occasionally
  }
}

/**
 * Close streaming mode on a card
 */
export async function closeStreamingMode(
  credentials: FeishuStreamingCredentials,
  cardId: string,
  sequence: number,
  finalSummary?: string,
): Promise<void> {
  // Build config object - summary must be set to clear "[Generating...]"
  const configObj: Record<string, unknown> = {
    streaming_mode: false,
    summary: { content: finalSummary || "" },
  };

  const settings = { config: configObj };

  const apiBase = getApiBaseUrl(credentials.appType);
  const response = await fetch(`${apiBase}/cardkit/v1/cards/${cardId}/settings`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${await getTenantAccessToken(credentials)}`,
      "Content-Type": "application/json; charset=utf-8",
    },
    body: JSON.stringify({
      settings: JSON.stringify(settings),
      sequence,
      uuid: `close_${cardId}_${sequence}`,
    }),
  });

  // Check response
  const result = (await response.json()) as { code: number; msg: string };

  if (result.code !== 0) {
    console.warn(`[feishu] [STREAMING] Failed to close streaming mode: ${result.msg}`);
  } else {
    console.log(`[feishu] [STREAMING] Closed streaming mode for card: ${cardId}`);
  }
}

/**
 * High-level streaming card manager
 */
export class FeishuStreamingSession {
  private account: ResolvedFeishuAccount;
  private credentials: FeishuStreamingCredentials;
  private state: FeishuStreamingCardState | null = null;
  private updateQueue: Promise<void> = Promise.resolve();
  private closed = false;

  constructor(account: ResolvedFeishuAccount) {
    this.account = account;
    this.credentials = {
      appId: account.config.appId,
      appSecret: account.config.appSecret,
      appType: account.config.appType,
    };
  }

  /**
   * Start a streaming session - creates and sends a streaming card
   */
  async start(
    receiveId: string,
    receiveIdType: "open_id" | "user_id" | "union_id" | "email" | "chat_id" = "chat_id",
    title?: string,
  ): Promise<void> {
    if (this.state) {
      console.warn("[feishu] [STREAMING] Streaming session already started");
      return;
    }

    try {
      const { cardId } = await createStreamingCard(this.credentials, title);
      const { messageId } = await sendStreamingCard(this.account, receiveId, cardId, receiveIdType);

      this.state = {
        cardId,
        messageId,
        sequence: 1,
        elementId: "streaming_content",
        currentText: "",
      };

      console.log(`[feishu] [STREAMING] Started streaming session: cardId=${cardId}, messageId=${messageId}`);
    } catch (err) {
      console.error(`[feishu] [STREAMING] Failed to start streaming session: ${String(err)}`);
      throw err;
    }
  }

  /**
   * Update the streaming card with new text (appends to existing)
   */
  async update(text: string): Promise<void> {
    if (!this.state || this.closed) {
      return;
    }

    // Queue updates to ensure order
    this.updateQueue = this.updateQueue.then(async () => {
      if (!this.state || this.closed) {
        return;
      }

      this.state.currentText = text;
      this.state.sequence += 1;

      try {
        await updateStreamingCardText(
          this.credentials,
          this.state.cardId,
          this.state.elementId,
          text,
          this.state.sequence,
        );
      } catch (err) {
        console.log(`[feishu] [STREAMING] Streaming update failed (will retry): ${String(err)}`);
      }
    });

    await this.updateQueue;
  }

  /**
   * Finalize and close streaming session
   */
  async close(finalText?: string, summary?: string): Promise<void> {
    if (!this.state || this.closed) {
      return;
    }
    this.closed = true;

    // Wait for pending updates
    await this.updateQueue;

    const text = finalText ?? this.state.currentText;
    this.state.sequence += 1;

    try {
      // Update final text
      if (text) {
        await updateStreamingCardText(
          this.credentials,
          this.state.cardId,
          this.state.elementId,
          text,
          this.state.sequence,
        );
      }

      // Close streaming mode
      this.state.sequence += 1;
      await closeStreamingMode(
        this.credentials,
        this.state.cardId,
        this.state.sequence,
        summary ?? truncateForSummary(text),
      );

      console.log(`[feishu] [STREAMING] Closed streaming session: cardId=${this.state.cardId}`);
    } catch (err) {
      console.error(`[feishu] [STREAMING] Failed to close streaming session: ${String(err)}`);
    }
  }

  /**
   * Check if session is active
   */
  isActive(): boolean {
    return this.state !== null && !this.closed;
  }

  /**
   * Get the message ID of streaming card
   */
  getMessageId(): string | null {
    return this.state?.messageId ?? null;
  }
}

/**
 * Truncate text to create a summary for chat preview
 */
function truncateForSummary(text: string, maxLength: number = 50): string {
  if (!text) {
    return "";
  }
  const cleaned = text.replace(/\n/g, " ").trim();
  if (cleaned.length <= maxLength) {
    return cleaned;
  }
  return cleaned.slice(0, maxLength - 3) + "...";
}
