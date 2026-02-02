import type {
  FeishuEvent,
  FeishuMessageContent,
} from "./types.js";
import type { ResolvedFeishuAccount } from "./types.config.js";
import { getFeishuRuntimeState, setFeishuMonitor, removeFeishuMonitor } from "./runtime.js";

// Event handler callback type
export type FeishuEventHandler = (event: {
  accountId: string;
  eventType: string;
  senderId?: string;
  senderName?: string;
  chatId?: string;
  chatType?: string;
  messageId?: string;
  messageContent?: FeishuMessageContent;
  rawEvent: FeishuEvent;
}) => Promise<void>;

// Event handlers map
const eventHandlers = new Map<string, FeishuEventHandler>();

// Store webhook path and account ID mapping
const webhookPaths = new Map<string, string>(); // path -> accountId

/**
 * Register event handler
 */
export const registerFeishuEventHandler = (accountId: string, handler: FeishuEventHandler): void => {
  eventHandlers.set(accountId, handler);
  console.log(`[feishu] Event handler registered for account: ${accountId}`);
};

/**
 * Unregister event handler
 */
export const unregisterFeishuEventHandler = (accountId: string): void => {
  eventHandlers.delete(accountId);
};

/**
 * Get webhook path for account
 */
export const resolveFeishuWebhookPath = (account: ResolvedFeishuAccount): string => {
  if (account.config.webhookPath) {
    return account.config.webhookPath.startsWith("/")
      ? account.config.webhookPath
      : `/${account.config.webhookPath}`;
  }
  return `/feishu/${account.accountId}`;
};

/**
 * Handle Feishu webhook event
 */
const handleFeishuEvent = async (
  accountId: string,
  event: FeishuEvent
): Promise<void> => {
  const handler = eventHandlers.get(accountId);
  if (!handler) {
    console.warn(`No event handler registered for Feishu account: ${accountId}`);
    return;
  }

  const eventType = event.header?.event_type || "unknown";
  const sender = event.event?.sender;
  const message = event.event?.message;

  // Extract sender_id correctly - it's nested in sender_id.open_id
  const senderId = sender?.sender_id?.open_id || sender?.user_id;
  const senderName = sender?.sender_id?.name || sender?.name;

  console.log(`[feishu] Processing message from ${senderId} in ${message?.chat_type}:`, message?.content);

  await handler({
    accountId,
    eventType,
    senderId,
    senderName,
    chatId: message?.chat_id,
    chatType: message?.chat_type,
    messageId: message?.message_id,
    messageContent: message?.content ? JSON.parse(message.content) : undefined,
    rawEvent: event,
  });
};

/**
 * Process incoming webhook request
 */
export const processFeishuWebhook = async (
  pathname: string,
  body: any
): Promise<{ statusCode: number; data: any }> => {
  // Find account by webhook path
  const accountId = webhookPaths.get(pathname);
  if (!accountId) {
    return { statusCode: 404, data: { code: 404, msg: "Webhook path not found" } };
  }

  try {
    // Handle URL verification (for initial webhook setup)
    if (body.challenge) {
      console.log(`[feishu] URL verification challenge received for account ${accountId}`);
      return { statusCode: 200, data: { challenge: body.challenge } };
    }

    // Handle regular events
    const event = body as FeishuEvent;
    
    // Process message events
    if (event.header?.event_type === "im.message.receive_v1") {
      await handleFeishuEvent(accountId, event);
    }

    return { statusCode: 200, data: { code: 0, msg: "success" } };
  } catch (error) {
    console.error(`Error handling Feishu webhook for ${accountId}:`, error);
    return { statusCode: 500, data: { code: 500, msg: "Internal server error" } };
  }
};

/**
 * Start Feishu webhook monitor (registers paths)
 */
export const startFeishuMonitor = async ({
  account,
  port,
  onEvent,
  onError,
}: {
  account: ResolvedFeishuAccount;
  port: number;
  onEvent?: FeishuEventHandler;
  onError?: (error: Error) => void;
}): Promise<void> => {
  const webhookPath = resolveFeishuWebhookPath(account);
  const accountId = account.accountId;

  // Check if already running
  const existing = getFeishuRuntimeState().monitors.get(accountId);
  if (existing) {
    throw new Error(`Feishu monitor already running for account: ${accountId}`);
  }

  // Register event handler
  if (onEvent) {
    registerFeishuEventHandler(accountId, onEvent);
  }

  // Register webhook path
  webhookPaths.set(webhookPath, accountId);

  console.log(
    `Feishu webhook monitor registered for account ${accountId}, path: ${webhookPath}`
  );

  // Store monitor state
  setFeishuMonitor(accountId, {
    accountId,
    webhookPath,
  });
};

/**
 * Stop Feishu webhook monitor
 */
export const stopFeishuMonitor = async (accountId: string): Promise<void> => {
  const monitor = getFeishuRuntimeState().monitors.get(accountId);
  if (monitor?.webhookPath) {
    webhookPaths.delete(monitor.webhookPath);
  }
  
  removeFeishuMonitor(accountId);
  unregisterFeishuEventHandler(accountId);
  console.log(`Feishu webhook monitor stopped for account: ${accountId}`);
};

/**
 * Stop all Feishu monitors
 */
export const stopAllFeishuMonitors = async (): Promise<void> => {
  const accountIds = getFeishuRuntimeState().monitors.keys();
  for (const accountId of accountIds) {
    await stopFeishuMonitor(accountId);
  }
};
