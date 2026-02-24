import type { ChannelId } from "clawdbot/plugin-sdk";

export const FeishuChannelId: ChannelId = "feishu";

export type FeishuCredentialSource = "env" | "config" | "none";

export type FeishuDmPolicy = "pairing" | "allowlist" | "blocklist";

export type FeishuReplyToMode = "off" | "all" | "op";

export type FeishuAccountConfig = {
  enabled?: boolean;
  name?: string;

  // Feishu app credentials
  appId?: string;
  appSecret?: string;
  appType?: "self_build" | "app_store";

  // Webhook configuration
  verifyToken?: string;
  encryptKey?: string;

  // Routing
  webhookPath?: string;
  webhookUrl?: string;

  // Direct message policy
  dm?: {
    policy?: FeishuDmPolicy;
    allowFrom?: Array<string>;
  };

  // Group message policy
  groupPolicy?: "allowlist" | "blocklist" | "all";
  allowList?: Array<string>;
  blockList?: Array<string>;

  // Threading
  replyToMode?: FeishuReplyToMode;

  // Rate limiting
  rateLimit?: {
    maxMessages?: number;
    windowMs?: number;
  };
};

export type FeishuConfig = Record<string, unknown> & FeishuAccountConfig;

export type ResolvedFeishuAccount = {
  accountId: string;
  name: string;
  enabled: boolean;
  credentialSource: FeishuCredentialSource;
  config: {
    appId: string;
    appSecret: string;
    appType?: "self_build" | "app_store";
    webhookPath?: string;
    webhookUrl?: string;
    dm?: {
      policy?: FeishuDmPolicy;
      allowFrom?: Array<string>;
    };
    groupPolicy?: "allowlist" | "blocklist" | "all";
    allowList?: Array<string>;
    blockList?: Array<string>;
    replyToMode?: FeishuReplyToMode;
  };
};

export type FeishuRuntimeState = {
  monitors: Map<string, FeishuMonitor>;
};

export type FeishuMonitor = {
  accountId: string;
  webhookPath: string;
  server?: any;
};
