import {
  type MoltbotConfig,
  DEFAULT_ACCOUNT_ID,
} from "clawdbot/plugin-sdk";
import type {
  FeishuConfig,
  ResolvedFeishuAccount,
  FeishuAccountConfig,
  FeishuCredentialSource,
} from "./types.config.js";
import { resolveCredentialSource } from "./auth.js";

/**
 * Get config value from section or account
 */
const getConfigValue = (
  section: FeishuConfig | undefined,
  accountId: string,
  key: string
): unknown => {
  // Try account-specific config first
  const accountConfig = section?.accounts?.[accountId] as FeishuAccountConfig | undefined;
  if (accountConfig && (accountConfig as any)[key] !== undefined) {
    return (accountConfig as any)[key];
  }
  // Fallback to top-level config
  return (section as any)?.[key];
};

/**
 * List all Feishu account IDs from config
 */
export const listFeishuAccountIds = (cfg: MoltbotConfig): string[] => {
  const accounts = (cfg.channels?.["feishu"] as FeishuConfig | undefined)?.accounts;
  if (accounts) {
    return Object.keys(accounts);
  }

  // Check if there's a top-level configuration (legacy single account)
  const topLevel = cfg.channels?.["feishu"] as FeishuConfig | undefined;
  if (topLevel && (topLevel.appId || topLevel.appSecret)) {
    return [DEFAULT_ACCOUNT_ID];
  }

  return [];
};

/**
 * Resolve default Feishu account ID
 */
export const resolveDefaultFeishuAccountId = (cfg: MoltbotConfig): string | undefined => {
  const accountIds = listFeishuAccountIds(cfg);
  if (accountIds.length === 0) return undefined;
  if (accountIds.length === 1) return accountIds[0];

  // Try to find enabled account
  for (const accountId of accountIds) {
    const account = resolveFeishuAccount({ cfg, accountId });
    if (account.enabled) {
      return accountId;
    }
  }

  return accountIds[0];
};

/**
 * Resolve Feishu account configuration
 */
export const resolveFeishuAccount = ({
  cfg,
  accountId = DEFAULT_ACCOUNT_ID,
}: {
  cfg: MoltbotConfig;
  accountId?: string;
}): ResolvedFeishuAccount => {
  const section = cfg.channels?.["feishu"] as FeishuConfig | undefined;

  const appId = getConfigValue(section, accountId, "appId") as string | undefined;
  const appSecret = getConfigValue(section, accountId, "appSecret") as string | undefined;
  const appType = (getConfigValue(section, accountId, "appType") as
    | "self_build"
    | "app_store"
    | undefined) ?? "self_build";
  const enabled = getConfigValue(section, accountId, "enabled") as boolean | undefined;
  const name = getConfigValue(section, accountId, "name") as string | undefined;
  const webhookPath = getConfigValue(section, accountId, "webhookPath") as
    | string
    | undefined;
  const webhookUrl = getConfigValue(section, accountId, "webhookUrl") as string | undefined;

  // Get nested config values
  const accountConfig = section?.accounts?.[accountId] as FeishuAccountConfig | undefined;
  const topLevelConfig = section as FeishuAccountConfig | undefined;

  const dmPolicy = (accountConfig?.dm?.policy || topLevelConfig?.dm?.policy ||
    "pairing") as "pairing" | "allowlist" | "blocklist";
  const dmAllowFrom = (accountConfig?.dm?.allowFrom || topLevelConfig?.dm?.allowFrom ||
    []) as Array<string>;

  const groupPolicy = (getConfigValue(section, accountId, "groupPolicy") as
    | "allowlist"
    | "blocklist"
    | "all"
    | undefined) ?? "allowlist";
  const allowList = (getConfigValue(section, accountId, "allowList") as
    | Array<string>
    | undefined) ?? [];
  const blockList = (getConfigValue(section, accountId, "blockList") as
    | Array<string>
    | undefined) ?? [];

  const replyToMode = (getConfigValue(section, accountId, "replyToMode") as
    | "off"
    | "all"
    | "op"
    | undefined) ?? "off";

  const credentialSource: FeishuCredentialSource =
    appId && appSecret ? resolveCredentialSource({ config: { appId, appSecret } } as any) : "none";

  return {
    accountId,
    name: name || `Feishu (${accountId})`,
    enabled: enabled ?? true,
    credentialSource,
    config: {
      appId: appId || "",
      appSecret: appSecret || "",
      appType,
      webhookPath,
      webhookUrl,
      dm: {
        policy: dmPolicy,
        allowFrom: dmAllowFrom,
      },
      groupPolicy,
      allowList,
      blockList,
      replyToMode,
    },
  };
};
