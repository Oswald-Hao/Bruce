import {
  DEFAULT_ACCOUNT_ID,
  deleteAccountFromConfigSection,
  formatPairingApproveHint,
  getChatChannelMeta,
  missingTargetError,
  setAccountEnabledInConfigSection,
  type ChannelDock,
  type ChannelMessageActionAdapter,
  type ChannelPlugin,
  type MoltbotConfig,
} from "clawdbot/plugin-sdk";

import {
  listFeishuAccountIds,
  resolveDefaultFeishuAccountId,
  resolveFeishuAccount,
  type ResolvedFeishuAccount,
} from "./accounts.js";
import { feishuMessageActions } from "./actions.js";
import { sendFeishuMessage, uploadFeishuMedia, probeFeishu } from "./api.js";
import { feishuOnboardingAdapter } from "./onboarding.js";
import { getFeishuRuntimeState, getFeishuMonitor } from "./runtime.js";
import {
  resolveFeishuWebhookPath,
  startFeishuMonitor,
  stopFeishuMonitor,
} from "./monitor.js";
import {
  normalizeFeishuTarget,
  formatFeishuTarget,
  looksLikeFeishuTargetId,
} from "./targets.js";

const meta = getChatChannelMeta("feishu");

const formatAllowFromEntry = (entry: string) =>
  entry
    .trim()
    .replace(/^(feishu|lark|feishu-bot):/i, "")
    .replace(/^open_id:/i, "")
    .replace(/^user_id:/i, "")
    .toLowerCase();

/**
 * Feishu Channel Dock
 */
export const feishuDock: ChannelDock = {
  id: "feishu",
  capabilities: {
    chatTypes: ["direct", "group"],
    reactions: true,
    media: true,
    blockStreaming: false,
  },
  outbound: { textChunkLimit: 2000 },
  config: {
    resolveAllowFrom: ({ cfg, accountId }) =>
      (
        resolveFeishuAccount({ cfg: cfg as MoltbotConfig, accountId }).config.dm
          ?.allowFrom ?? []
      ).map((entry) => String(entry)),
    formatAllowFrom: ({ allowFrom }) =>
      allowFrom
        .map((entry) => String(entry))
        .filter(Boolean)
        .map(formatAllowFromEntry),
  },
  groups: {
    resolveRequireMention: () => false,
  },
};

/**
 * Feishu Channel Plugin
 */
export const feishuPlugin: ChannelPlugin<ResolvedFeishuAccount> = {
  id: "feishu",
  meta: { ...meta },
  onboarding: feishuOnboardingAdapter,
  pairing: {
    idLabel: "feishuUserId",
    normalizeAllowEntry: (entry) => formatAllowFromEntry(entry),
    notifyApproval: async ({ cfg, id }) => {
      const account = resolveFeishuAccount({ cfg: cfg as MoltbotConfig });
      if (account.credentialSource === "none") return;

      const user = normalizeFeishuTarget(id) ?? id;
      const target = formatFeishuTarget(user);

      await sendFeishuMessage({
        account,
        receiveId: target.receiveId,
        receiveIdType: target.receiveIdType,
        msgType: "text",
        content: JSON.stringify({ text: "✓ Pairing approved. You can now send messages." }),
      });
    },
  },
  capabilities: {
    chatTypes: ["direct", "group"],
    reactions: true,
    media: true,
    nativeCommands: false,
    blockStreaming: false,
  },
  reload: { configPrefixes: ["channels.feishu"] },
  config: {
    listAccountIds: (cfg) => listFeishuAccountIds(cfg as MoltbotConfig),
    resolveAccount: (cfg, accountId) =>
      resolveFeishuAccount({ cfg: cfg as MoltbotConfig, accountId }),
    defaultAccountId: (cfg) => resolveDefaultFeishuAccountId(cfg as MoltbotConfig),
    setAccountEnabled: ({ cfg, accountId, enabled }) =>
      setAccountEnabledInConfigSection({
        cfg: cfg as MoltbotConfig,
        sectionKey: "feishu",
        accountId,
        enabled,
        allowTopLevel: true,
      }),
    deleteAccount: ({ cfg, accountId }) =>
      deleteAccountFromConfigSection({
        cfg: cfg as MoltbotConfig,
        sectionKey: "feishu",
        accountId,
        clearBaseFields: [
          "appId",
          "appSecret",
          "appType",
          "verifyToken",
          "encryptKey",
          "webhookPath",
          "webhookUrl",
          "name",
        ],
      }),
    isConfigured: (account) => account.credentialSource !== "none",
    describeAccount: (account) => ({
      accountId: account.accountId,
      name: account.name,
      enabled: account.enabled,
      configured: account.credentialSource !== "none",
      credentialSource: account.credentialSource,
    }),
    resolveAllowFrom: ({ cfg, accountId }) =>
      (
        resolveFeishuAccount({
          cfg: cfg as MoltbotConfig,
          accountId,
        }).config.dm?.allowFrom ?? []
      ).map((entry) => String(entry)),
    formatAllowFrom: ({ allowFrom }) =>
      allowFrom
        .map((entry) => String(entry))
        .filter(Boolean)
        .map(formatAllowFromEntry),
  },
  security: {
    resolveDmPolicy: ({ cfg, accountId, account }) => {
      const resolvedAccountId = accountId ?? account.accountId ?? DEFAULT_ACCOUNT_ID;
      const useAccountPath = Boolean(
        (cfg as MoltbotConfig).channels?.["feishu"]?.accounts?.[resolvedAccountId]
      );
      const allowFromPath = useAccountPath
        ? `channels.feishu.accounts.${resolvedAccountId}.dm.`
        : "channels.feishu.dm.";
      return {
        policy: account.config.dm?.policy ?? "pairing",
        allowFrom: account.config.dm?.allowFrom ?? [],
        allowFromPath,
        approveHint: formatPairingApproveHint("feishu"),
        normalizeEntry: (raw) => formatAllowFromEntry(raw),
      };
    },
    collectWarnings: ({ account, cfg }) => {
      const warnings: string[] = [];
      const defaultGroupPolicy = cfg.channels?.defaults?.groupPolicy;
      const groupPolicy = account.config.groupPolicy ?? defaultGroupPolicy ?? "allowlist";

      if (groupPolicy === "allowlist" && (!account.config.allowList || account.config.allowList.length === 0)) {
        warnings.push(
          "Group policy is set to allowlist, but no groups are allowed. Bot will not respond to group messages."
        );
      }

      return warnings;
    },
  },
  outbound: {
    sendText: async ({ cfg, to, text, accountId }) => {
      if (!to) {
        throw missingTargetError({ channel: "Feishu" });
      }

      const account = resolveFeishuAccount({ cfg: cfg as MoltbotConfig, accountId });

      const normalizedTarget = normalizeFeishuTarget(to);
      if (!normalizedTarget) {
        throw new Error(`Invalid Feishu target: ${to}`);
      }

      const formatted = formatFeishuTarget(normalizedTarget);

      const content = JSON.stringify({ text });

      await sendFeishuMessage({
        account,
        receiveId: formatted.receiveId,
        receiveIdType: formatted.receiveIdType,
        msgType: "text",
        content,
      });

      return {
        channelId: normalizedTarget,
        messageTs: Date.now().toString(),
      };
    },
    updateText: async ({ cfg, to, messageId, text, accountId }) => {
      if (!to) {
        throw missingTargetError({ channel: "Feishu" });
      }

      const account = resolveFeishuAccount({ cfg: cfg as MoltbotConfig, accountId });

      const content = JSON.stringify({ text });

      await updateFeishuMessage({
        account,
        messageId,
        msgType: "text",
        content,
      });

      return {
        channelId: to,
        messageTs: Date.now().toString(),
      };
    },
    sendMedia: async ({ cfg, to, mediaUrl, accountId }) => {
      if (!to) {
        throw missingTargetError({ channel: "Feishu" });
      }

      const account = resolveFeishuAccount({ cfg: cfg as MoltbotConfig, accountId });

      const normalizedTarget = normalizeFeishuTarget(to);
      if (!normalizedTarget) {
        throw new Error(`Invalid Feishu target: ${to}`);
      }

      const formatted = formatFeishuTarget(normalizedTarget);

      // Fetch media from URL and upload
      const response = await fetch(mediaUrl);
      const buffer = Buffer.from(await response.arrayBuffer());

      const fileKey = await uploadFeishuMedia({
        account,
        file: buffer,
        fileType: "image",
      });

      const content = JSON.stringify({ image_key: fileKey });

      await sendFeishuMessage({
        account,
        receiveId: formatted.receiveId,
        receiveIdType: formatted.receiveIdType,
        msgType: "image",
        content,
      });

      return {
        channelId: normalizedTarget,
        messageTs: Date.now().toString(),
      };
    },
  },
  status: {
    probe: async ({ account }) => {
      return await probeFeishu({ account });
    },
  },
  gateway: {
    startAccount: async ({ account, setStatus }) => {
      // Webhook is registered via plugin.registerHttpHandler in index.ts
      // Just mark the account as running
      setStatus({
        accountId: account.accountId,
        running: true,
      });
      console.log(`[feishu] Account ${account.accountId} started (webhook mode)`);
    },
    stopAccount: async ({ accountId }) => {
      // Webhook handler will be removed when plugin is unloaded
      await stopFeishuMonitor(accountId);
    },
    getHealth: async ({ accountId }) => {
      // Webhook mode is always "healthy" if the plugin is loaded
      return {
        running: true,
        hasWebhook: true,
        webhookPath: resolveFeishuWebhookPath({ accountId } as any),
      };
    },
  },
  actions: feishuMessageActions,
};

export default feishuPlugin;
