import type { ResolvedFeishuAccount } from "./types.config.js";

/**
 * Feishu target formats:
 * - Direct message: "open_id:ou_xxxxxxxxxxxxxxxx" or "user_id:xxxxxxxxxxxxxx"
 * - Group chat: "chat_id:oc_xxxxxxxxxxxxxxxx"
 * - Simple format (defaults to open_id): "ou_xxxxxxxxxxxxxxxx" or "oc_xxxxxxxxxxxxxxxx"
 */

const FEISHU_PREFIXES = ["feishu", "lark", "feishu-bot"];

/**
 * Normalize Feishu target by removing prefix and extracting ID
 */
export const normalizeFeishuTarget = (target: string): string | null => {
  if (!target || typeof target !== "string") return null;

  const normalized = target.trim();

  // Remove prefix if present
  for (const prefix of FEISHU_PREFIXES) {
    if (normalized.toLowerCase().startsWith(`${prefix}:`)) {
      return normalized.substring(prefix.length + 1);
    }
  }

  // Remove explicit type prefix
  if (normalized.startsWith("open_id:")) {
    return normalized.substring(8);
  }
  if (normalized.startsWith("user_id:")) {
    return normalized.substring(8);
  }
  if (normalized.startsWith("union_id:")) {
    return normalized.substring(9);
  }
  if (normalized.startsWith("chat_id:")) {
    return normalized.substring(8);
  }

  // Return as-is if it looks like a Feishu ID
  if (normalized.startsWith("ou_") || normalized.startsWith("oc_") || normalized.startsWith("on_")) {
    return normalized;
  }

  return normalized;
};

/**
 * Check if target is a user (open_id)
 */
export const isFeishuUserTarget = (target: string): boolean => {
  const normalized = normalizeFeishuTarget(target);
  return normalized?.startsWith("ou_") ?? false;
};

/**
 * Check if target is a chat (group)
 */
export const isFeishuChatTarget = (target: string): boolean => {
  const normalized = normalizeFeishuTarget(target);
  return normalized?.startsWith("oc_") ?? false;
};

/**
 * Format target for API call
 */
export const formatFeishuTarget = (target: string): {
  receiveId: string;
  receiveIdType: "open_id" | "user_id" | "union_id" | "chat_id";
  msgType: "text" | "post";
} => {
  const normalized = normalizeFeishuTarget(target);

  if (!normalized) {
    throw new Error(`Invalid Feishu target: ${target}`);
  }

  // Determine target type
  if (normalized.startsWith("ou_")) {
    return {
      receiveId: normalized,
      receiveIdType: "open_id",
      msgType: "text",
    };
  }

  if (normalized.startsWith("on_")) {
    return {
      receiveId: normalized,
      receiveIdType: "union_id",
      msgType: "text",
    };
  }

  if (normalized.startsWith("oc_")) {
    // Group chat
    return {
      receiveId: normalized,
      receiveIdType: "chat_id",
      msgType: "text",
    };
  }

  // Default to open_id
  return {
    receiveId: normalized,
    receiveIdType: "open_id",
    msgType: "text",
  };
};

/**
 * Check if a string looks like a Feishu target ID
 */
export const looksLikeFeishuTargetId = (raw: string, normalized?: string): boolean => {
  const trimmed = raw.trim();
  if (!trimmed) return false;

  // Check if it starts with Feishu ID prefixes
  if (trimmed.startsWith("ou_") || trimmed.startsWith("oc_") || trimmed.startsWith("on_")) {
    return true;
  }

  // Check if it has explicit type prefixes
  if (/^open_id:/i.test(trimmed) || /^user_id:/i.test(trimmed) ||
      /^union_id:/i.test(trimmed) || /^chat_id:/i.test(trimmed)) {
    return true;
  }

  // Check if it has channel prefix
  if (/^(feishu|lark|feishu-bot):/i.test(trimmed)) {
    return true;
  }

  return false;
};

/**
 * Resolve target display name
 */
export const resolveFeishuTargetDisplayName = ({
  account,
  target,
}: {
  account: ResolvedFeishuAccount;
  target: string;
}): string => {
  const normalized = normalizeFeishuTarget(target);

  if (!normalized) {
    return target;
  }

  // For now, return the normalized ID
  // In production, you might want to fetch user/chat info to get the display name
  return normalized;
};
