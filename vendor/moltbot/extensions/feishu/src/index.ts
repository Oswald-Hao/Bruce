export { feishuDock, feishuPlugin, feishuPlugin as default } from "./channel.js";
export {
  listFeishuAccountIds,
  resolveDefaultFeishuAccountId,
  resolveFeishuAccount,
} from "./accounts.js";
export {
  getTenantAccessToken,
  sendFeishuMessage,
  uploadFeishuMedia,
  getFeishuUserInfo,
  getFeishuChatInfo,
  verifyFeishuWebhook,
  probeFeishu,
} from "./api.js";
export {
  validateFeishuCredentials,
  maskAppSecret,
  resolveCredentialSource,
} from "./auth.js";
export {
  normalizeFeishuTarget,
  isFeishuUserTarget,
  isFeishuChatTarget,
  formatFeishuTarget,
  resolveFeishuTargetDisplayName,
} from "./targets.js";
export {
  resolveFeishuWebhookPath,
  startFeishuMonitor,
  stopFeishuMonitor,
  stopAllFeishuMonitors,
  registerFeishuEventHandler,
  unregisterFeishuEventHandler,
} from "./monitor.js";
export { feishuOnboardingAdapter } from "./onboarding.js";
export {
  getFeishuRuntimeState,
  getFeishuMonitor,
  setFeishuMonitor,
  removeFeishuMonitor,
  getFeishuMonitorAccountIds,
} from "./runtime.js";
export {
  feishuMessageActions,
} from "./actions.js";

export type {
  FeishuUser,
  FeishuChatType,
  FeishuEvent,
  FeishuMessageContent,
  FeishuPostContent,
  FeishuPostElement,
  FeishuSendMessageRequest,
  FeishuSendMessageResponse,
  FeishuUserInfo,
  FeishuChatInfo,
  FeishuAttachment,
  FeishuMediaUploadResponse,
} from "./types.js";
export type {
  FeishuChannelId,
  FeishuCredentialSource,
  FeishuDmPolicy,
  FeishuReplyToMode,
  FeishuAccountConfig,
  FeishuConfig,
  ResolvedFeishuAccount,
  FeishuRuntimeState,
  FeishuMonitor,
} from "./types.config.js";
