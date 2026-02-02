import type { ResolvedFeishuAccount, FeishuCredentialSource } from "./types.config.js";

/**
 * Determine credential source for Feishu account
 */
export const resolveCredentialSource = (
  account: ResolvedFeishuAccount
): FeishuCredentialSource => {
  if (account.config.appId && account.config.appSecret) {
    return "config";
  }
  return "none";
};

/**
 * Validate Feishu credentials format
 */
export const validateFeishuCredentials = ({
  appId,
  appSecret,
}: {
  appId?: string;
  appSecret?: string;
}): { valid: boolean; error?: string } => {
  if (!appId || !appId.trim()) {
    return { valid: false, error: "App ID is required" };
  }

  if (!appSecret || !appSecret.trim()) {
    return { valid: false, error: "App Secret is required" };
  }

  // Feishu App ID format: cli_xxxxxxxxxxxxxxxx
  if (!/^cli_[a-zA-Z0-9]{28}$/.test(appId)) {
    return {
      valid: false,
      error: "Invalid App ID format (should be cli_ followed by 28 alphanumeric characters)",
    };
  }

  // App Secret should be at least 20 characters
  if (appSecret.length < 20) {
    return {
      valid: false,
      error: "App Secret is too short (should be at least 20 characters)",
    };
  }

  return { valid: true };
};

/**
 * Mask sensitive credential data for logging
 */
export const maskAppSecret = (secret: string): string => {
  if (secret.length <= 8) {
    return "*".repeat(secret.length);
  }
  return `${secret.substring(0, 4)}${"*".repeat(secret.length - 8)}${secret.substring(secret.length - 4)}`;
};
