import type { MoltbotPluginApi } from "clawdbot/plugin-sdk";
import { emptyPluginConfigSchema } from "clawdbot/plugin-sdk";

import { feishuDock, feishuPlugin } from "./src/channel.js";
import { resolveFeishuWebhookPath } from "./src/monitor.js";
import { resolveFeishuAccount } from "./src/accounts.js";
import { loadConfig } from "../../src/config/config.js";

// Pre-import dispatch modules to avoid slow dynamic imports
import { dispatchInboundMessage } from "../../src/auto-reply/dispatch.js";
import { sendFeishuMessage, uploadFeishuImage, uploadFeishuMedia, updateFeishuMessage, addTypingIndicator, removeReaction, getFeishuChatMemberCount } from "./src/api.js";

// Message deduplication cache (persisted to disk)
import { readFileSync, writeFileSync, existsSync, mkdirSync, unlinkSync, statSync } from "node:fs";
import { join } from "node:path";

const CACHE_DIR = join(process.env.HOME || "", ".clawdbot", "feishu");
const CACHE_FILE = join(CACHE_DIR, "dedup-cache.json");
const CACHE_TTL = 7 * 24 * 60 * 60 * 1000; // 7 days in ms

interface CacheEntry {
  messageId: string;
  timestamp: number;
}

// Load cache from disk on startup
let messageCache = new Map<string, number>();
let cacheCleanupTimer: NodeJS.Timeout | null = null;

function loadCacheFromDisk() {
  try {
    if (existsSync(CACHE_FILE)) {
      const data = readFileSync(CACHE_FILE, "utf-8");
      const entries = JSON.parse(data) as CacheEntry[];
      const now = Date.now();
      messageCache = new Map();
      let loaded = 0;
      let expired = 0;
      for (const entry of entries) {
        if (now - entry.timestamp < CACHE_TTL) {
          messageCache.set(entry.messageId, entry.timestamp);
          loaded++;
        } else {
          expired++;
        }
      }
      console.log(`[feishu] [DEDUP] Cache loaded from disk: ${loaded} entries, ${expired} expired`);
    } else {
      console.log(`[feishu] [DEDUP] No cache file found, starting fresh`);
    }
  } catch (error) {
    console.error(`[feishu] [DEDUP] Failed to load cache from disk:`, error);
    messageCache = new Map();
  }
}

function saveCacheToDisk() {
  try {
    if (!existsSync(CACHE_DIR)) {
      mkdirSync(CACHE_DIR, { recursive: true });
    }
    const entries = Array.from(messageCache.entries()).map(([messageId, timestamp]) => ({
      messageId,
      timestamp,
    }));
    writeFileSync(CACHE_FILE, JSON.stringify(entries), "utf-8");
  } catch (error) {
    console.error(`[feishu] [DEDUP] Failed to save cache to disk:`, error);
  }
}

function startCacheCleanup() {
  if (cacheCleanupTimer) return;
  cacheCleanupTimer = setInterval(() => {
    const now = Date.now();
    let removed = 0;
    for (const [messageId, timestamp] of messageCache.entries()) {
      if (now - timestamp > CACHE_TTL) {
        messageCache.delete(messageId);
        removed++;
      }
    }
    if (removed > 0) {
      console.log(`[feishu] [DEDUP] Cleaned up ${removed} expired entries (size: ${messageCache.size})`);
      saveCacheToDisk();
    }
  }, 60 * 60 * 1000); // Every hour
}

/**
 * Process Feishu message asynchronously (background processing)
 * This function is called AFTER the webhook response has been sent
 */
async function processFeishuMessageAsync(data: any) {
  console.log(`[feishu] ============================================`);
  console.log(`[feishu] [ASYNC] Starting background message processing`);
  console.log(`[feishu] ============================================`);

  const event = data;
  const eventType = event.header?.event_type || "unknown";
  const sender = event.event?.sender;
  const message = event.event?.message;

  // Extract sender_id correctly - it's nested in sender_id.open_id
  const senderId = sender?.sender_id?.open_id || sender?.user_id;
  const senderName = sender?.sender_id?.name || sender?.name;

  // CRITICAL: Reload account config to get fresh credentials
  const freshConfig = loadConfig();
  const account = resolveFeishuAccount({ cfg: freshConfig });
  const accountId = account.accountId;

  console.log(`[feishu] [ASYNC] [ACCOUNT] Account ID: ${accountId}`);
  console.log(`[feishu] [ASYNC] [ACCOUNT] App ID: ${account.config.appId ? account.config.appId.substring(0, 10) + '...' : 'MISSING'}`);
  console.log(`[feishu] [ASYNC] [ACCOUNT] App Secret: ${account.config.appSecret ? 'SET' : 'MISSING'}`);

  console.log(`[feishu] [ASYNC] [1/6] Message extracted: senderId=${senderId}, chatType=${message?.chat_type}`);

  // Extract original message ID for reply threading
  const originalMessageId = message?.message_id;
  console.log(`[feishu] [ASYNC] [1/6] Original message ID: ${originalMessageId}`);

  // For sending replies:
  // - P2P (private chat): use chat_id with chat_id type
  // - Group chat: use chat_id with chat_id type
  const channelId = message?.chat_id || senderId;
  const replyIdType = "chat_id";

  console.log(`[feishu] [ASYNC] [2/6] Reply target resolved: channelId=${channelId}, replyIdType=${replyIdType}`);

  // Create message context
  const msgContent = message?.content ? JSON.parse(message.content) : undefined;
  console.log(`[feishu] [ASYNC] [3/6] Message content parsed:`, msgContent);

  // Check for group member count query
  const textMessage = msgContent?.text || "";
  const memberCountKeywords = ["群里有几个人", "群里有几人", "群多少人", "有多少人", "成员数量"];
  const isMemberCountQuery = memberCountKeywords.some(keyword => textMessage.includes(keyword));

  if (isMemberCountQuery && message?.chat_type === "group") {
    try {
      console.log(`[feishu] [ASYNC] [3.5/6] Member count query detected, fetching...`);

      // Get member count
      const { count } = await getFeishuChatMemberCount({
        account,
        chatId: channelId,
      });

      console.log(`[feishu] [ASYNC] [3.5/6] Member count: ${count}`);

      // Send direct reply
      const replyText = `这个群里有 ${count} 个人。`;
      await sendFeishuMessage({
        account,
        receiveId: channelId,
        receiveIdType: "chat_id",
        msgType: "text",
        content: JSON.stringify({ text: replyText }),
      });

      console.log(`[feishu] [ASYNC] ✓ Sent member count reply`);

      // Skip AI processing for this query
      return;
    } catch (error) {
      console.error(`[feishu] [ASYNC] Failed to get member count:`, error);
      // Continue to AI processing if failed
    }
  }

  // Create a promise that resolves when AI processing is complete
  let resolveProcessing: ((value: void) => void) | null = null;
  const processingComplete = new Promise<void>((resolve) => {
    resolveProcessing = resolve;
  });

  // Track if sendFinalReply has been called to prevent duplicates
  let sendFinalCalled = false;
  let typingReactionId: string | null = null;

  // Function to send "typing" indicator (via emoji reaction)
  const sendThinkingCard = async () => {
    try {
      // Add "Typing" emoji reaction to user's message
      const reactionId = await addTypingIndicator({
        account,
        messageId: originalMessageId,
      });

      if (reactionId) {
        typingReactionId = reactionId;
        console.log(`[feishu] [ASYNC] ✓ Typing indicator added, reaction_id: ${typingReactionId}`);
      }
    } catch (error) {
      console.error(`[feishu] [ASYNC] ✗ Failed to add typing indicator:`, error);
    }
  };

  // Send thinking card immediately
  sendThinkingCard().catch((e) => {
    console.error(`[feishu] [ASYNC] Failed to send thinking card:`, e);
  });

  // Create dispatcher for sending replies
  console.log(`[feishu] [ASYNC] [4/6] Creating reply dispatcher...`);
  const dispatcher = {
    sendToolResult: async (payload) => {
      console.log(`[feishu] [ASYNC] [DISPATCHER] ========== sendToolResult CALLED ==========`);
      console.log(`[feishu] [ASYNC] [DISPATCHER] Payload:`, JSON.stringify(payload).substring(0, 200));

      try {
        // Handle both formats:
        // 1. New format: { text, media: [{ type, buffer }] }
        // 2. Legacy/browser format: { content: [{ type, text/data, mimeType }] }
        const isContentFormat = payload.content && Array.isArray(payload.content);
        const isMediaFormat = payload.media && Array.isArray(payload.media);

        let text = "";
        const mediaItems: Array<{ type: string; buffer: Buffer; mimeType?: string }> = [];

        if (isContentFormat) {
          // Process content array format (from browser tools)
          console.log(`[feishu] [ASYNC] [DISPATCHER] Processing content array format (${payload.content.length} items)`);

          for (const item of payload.content) {
            if (item.type === "text") {
              text += (text ? "\n" : "") + (item.text || "");
            } else if (item.type === "image" && item.data) {
              // Convert base64 to buffer
              const buffer = Buffer.from(item.data, "base64");
              mediaItems.push({
                type: "image",
                buffer,
                mimeType: item.mimeType || "image/png",
              });
              console.log(`[feishu] [ASYNC] [DISPATCHER] Found image: ${buffer.length} bytes, ${item.mimeType || "image/png"}`);
            } else if (item.type === "audio" && item.data) {
              const buffer = Buffer.from(item.data, "base64");
              mediaItems.push({
                type: "audio",
                buffer,
                mimeType: item.mimeType || "audio/mp3",
              });
            }
          }
        } else if (isMediaFormat) {
          // Process media format
          text = payload.text || "";
          for (const mediaItem of payload.media) {
            if (mediaItem.buffer) {
              mediaItems.push({
                type: mediaItem.type,
                buffer: mediaItem.buffer,
                mimeType: mediaItem.mimeType,
              });
            }
          }
        } else {
          // Text only
          text = payload.text || "";
        }

        // Send media attachments
        if (mediaItems.length > 0) {
          console.log(`[feishu] [ASYNC] [DISPATCHER] Sending ${mediaItems.length} media item(s)`);

          for (const mediaItem of mediaItems) {
            const mediaType = mediaItem.type; // "audio", "image", "file", etc.

            if (mediaType === "audio" || mediaType === "file") {
              try {
                console.log(`[feishu] [ASYNC] [DISPATCHER] Uploading ${mediaType} (${mediaItem.buffer.length} bytes)...`);
                const fileKey = await uploadFeishuMedia({
                  account,
                  file: mediaItem.buffer,
                  fileType: mediaType === "audio" ? "audio" : "file",
                });

                console.log(`[feishu] [ASYNC] [DISPATCHER] Sending ${mediaType} message...`);
                await sendFeishuMessage({
                  account,
                  receiveId: channelId,
                  receiveIdType: replyIdType,
                  msgType: mediaType === "audio" ? "audio" : "file",
                  content: { [`${mediaType}_key`]: fileKey },
                });
                console.log(`[feishu] [ASYNC] [DISPATCHER] ✓ ${mediaType} message sent successfully`);
              } catch (mediaError) {
                console.error(`[feishu] [ASYNC] [DISPATCHER] ✗ Failed to send ${mediaType}:`, mediaError);
              }
            } else if (mediaType === "image") {
              try {
                console.log(`[feishu] [ASYNC] [DISPATCHER] Uploading image (${mediaItem.buffer.length} bytes)...`);
                const imageKey = await uploadFeishuImage({
                  account,
                  imageBuffer: mediaItem.buffer,
                });

                console.log(`[feishu] [ASYNC] [DISPATCHER] Sending image message...`);
                await sendFeishuMessage({
                  account,
                  receiveId: channelId,
                  receiveIdType: replyIdType,
                  msgType: "image",
                  content: { image_key: imageKey },
                });
                console.log(`[feishu] [ASYNC] [DISPATCHER] ✓ Image message sent successfully`);
              } catch (imgError) {
                console.error(`[feishu] [ASYNC] [DISPATCHER] ✗ Failed to send image:`, imgError);
              }
            }
          }

          // Send text message along with media
          if (text) {
            await sendFeishuMessage({
              account,
              receiveId: channelId,
              receiveIdType: replyIdType,
              msgType: "text",
              content: { text },
            });
            console.log(`[feishu] [ASYNC] [DISPATCHER] ✓ Text message sent successfully`);
          }
        } else if (text) {
          // No media - just send text
          console.log(`[feishu] [ASYNC] [DISPATCHER] Sending tool result: ${text.substring(0, 100)}...`);
          await sendFeishuMessage({
            account,
            receiveId: channelId,
            receiveIdType: replyIdType,
            msgType: "text",
            content: { text },
          });
          console.log(`[feishu] [ASYNC] [DISPATCHER] ✓ Tool result sent successfully`);
        }

        return true;
      } catch (error) {
        console.error(`[feishu] [ASYNC] [DISPATCHER] ✗ Failed to send tool result:`, error);
        return false;
      }
    },
    sendBlockReply: async (payload) => {
      console.log(`[feishu] [ASYNC] [DISPATCHER] ========== sendBlockReply CALLED ==========`);
      console.log(`[feishu] [ASYNC] [DISPATCHER] Payload:`, JSON.stringify(payload).substring(0, 200));
      try {
        const text = payload.text || "";
        const hasMedia = payload.media && payload.media.length > 0;

        if (hasMedia) {
          // Has media attachments - upload and send as image
          console.log(`[feishu] [ASYNC] [DISPATCHER] Processing ${payload.media.length} media attachment(s)`);

          for (const mediaItem of payload.media) {
            if (mediaItem.type === "image" && mediaItem.buffer) {
              try {
                console.log(`[feishu] [ASYNC] [DISPATCHER] Uploading image (${mediaItem.buffer.length} bytes)...`);
                const imageKey = await uploadFeishuImage({
                  account,
                  imageBuffer: mediaItem.buffer,
                });

                console.log(`[feishu] [ASYNC] [DISPATCHER] Sending image message...`);
                await sendFeishuMessage({
                  account,
                  receiveId: channelId,
                  receiveIdType: replyIdType,
                  msgType: "image",
                  content: { image_key: imageKey },
                });
                console.log(`[feishu] [ASYNC] [DISPATCHER] ✓ Image message sent successfully`);
              } catch (imgError) {
                console.error(`[feishu] [ASYNC] [DISPATCHER] ✗ Failed to send image:`, imgError);
                // Fall through to send text message instead
              }
            }
          }

          // Send text message along with images
          if (text) {
            await sendFeishuMessage({
              account,
              receiveId: channelId,
              receiveIdType: replyIdType,
              msgType: "text",
              content: { text },
            });
            console.log(`[feishu] [ASYNC] [DISPATCHER] ✓ Text message sent successfully`);
          }
        } else {
          // No media - just send text
          console.log(`[feishu] [ASYNC] [DISPATCHER] Sending block reply: ${text.substring(0, 100)}...`);
          await sendFeishuMessage({
            account,
            receiveId: channelId,
            receiveIdType: replyIdType,
            msgType: "text",
            content: { text },
          });
          console.log(`[feishu] [ASYNC] [DISPATCHER] ✓ Block reply sent successfully`);
        }
        return true;
      } catch (error) {
        console.error(`[feishu] [ASYNC] [DISPATCHER] ✗ Failed to send block reply:`, error);
        return false;
      }
    },
    sendFinalReply: async (payload) => {
      // Prevent duplicate calls
      if (sendFinalCalled) {
        console.log(`[feishu] [ASYNC] [DISPATCHER] ⚠ sendFinalReply already called, skipping duplicate`);
        return;
      }
      sendFinalCalled = true;

      console.log(`[feishu] [ASYNC] [DISPATCHER] ========== sendFinalReply CALLED ==========`);
      console.log(`[feishu] [ASYNC] [DISPATCHER] Payload:`, JSON.stringify(payload).substring(0, 200));

      try {
        const text = payload.text || "";
        const hasMedia = payload.media && payload.media.length > 0;

        // Auto-detect and send screenshot if Agent created one
        // IMPORTANT: Only send screenshots created recently (within last 60 seconds)
        // to avoid sending old cached files from previous conversations
        const possiblePaths = [
          "/tmp/current_desktop.png",
          "/tmp/desktop_screenshot.png",
          "/tmp/screenshot.png",
          "/tmp/desktop_new.png",
          "/tmp/screenshot_latest.png",
          "/tmp/after_wake.png",
          "/tmp/screen_now.png",
          join(process.env.HOME || "", "clawd", "screenshot.png"),
        ];

        const now = Date.now();
        const MAX_SCREENSHOT_AGE_MS = 60 * 1000; // 60 seconds

        // Find all existing screenshots that were created recently
        const existingShots: { path: string; mtime: number; age: number }[] = [];
        for (const path of possiblePaths) {
          if (existsSync(path)) {
            try {
              const stat = statSync(path);
              const age = now - stat.mtimeMs;
              if (age < MAX_SCREENSHOT_AGE_MS) {
                existingShots.push({ path, mtime: stat.mtimeMs, age });
                console.log(`[feishu] [ASYNC] [DISPATCHER] 📸 Found recent screenshot: ${path} (${Math.round(age / 1000)}s ago)`);
              } else {
                console.log(`[feishu] [ASYNC] [DISPATCHER] ⏭ Skipping old screenshot: ${path} (${Math.round(age / 1000)}s ago)`);
              }
            } catch (e) {
              console.error(`[feishu] [ASYNC] [DISPATCHER] Failed to stat ${path}:`, e);
            }
          }
        }

        // Sort by modification time, newest first
        existingShots.sort((a, b) => b.mtime - a.mtime);

        const foundScreenshot = existingShots.length > 0 ? existingShots[0].path : null;

        if (foundScreenshot) {
          console.log(`[feishu] [ASYNC] [DISPATCHER] 📸 Auto-detected NEWEST screenshot: ${foundScreenshot}`);
          try {
            const imageBuffer = readFileSync(foundScreenshot);
            console.log(`[feishu] [ASYNC] [DISPATCHER] Uploading screenshot (${imageBuffer.length} bytes)...`);

            const imageKey = await uploadFeishuImage({
              account,
              imageBuffer: imageBuffer,
            });

            console.log(`[feishu] [ASYNC] [DISPATCHER] Sending screenshot message...`);
            await sendFeishuMessage({
              account,
              receiveId: channelId,
              receiveIdType: replyIdType,
              msgType: "image",
              content: { image_key: imageKey },
            });
            console.log(`[feishu] [ASYNC] [DISPATCHER] ✓ Screenshot sent successfully!`);

            // Clean up temporary screenshot file (only if still exists)
            try {
              if (existsSync(foundScreenshot)) {
                unlinkSync(foundScreenshot);
                console.log(`[feishu] [ASYNC] [DISPATCHER] ✓ Cleaned up ${foundScreenshot}`);
              } else {
                console.log(`[feishu] [ASYNC] [DISPATCHER] ℹ File already deleted: ${foundScreenshot}`);
              }
            } catch (cleanupError) {
              console.error(`[feishu] [ASYNC] [DISPATCHER] Failed to clean up screenshot:`, cleanupError);
            }
          } catch (screenshotError) {
            console.error(`[feishu] [ASYNC] [DISPATCHER] ✗ Failed to send screenshot:`, screenshotError);
          }
        }

        if (hasMedia) {
          // Has media attachments - upload and send as image
          console.log(`[feishu] [ASYNC] [DISPATCHER] Processing ${payload.media.length} media attachment(s)`);

          for (const mediaItem of payload.media) {
            if (mediaItem.type === "image" && mediaItem.buffer) {
              try {
                console.log(`[feishu] [ASYNC] [DISPATCHER] Uploading image (${mediaItem.buffer.length} bytes)...`);
                const imageKey = await uploadFeishuImage({
                  account,
                  imageBuffer: mediaItem.buffer,
                });

                console.log(`[feishu] [ASYNC] [DISPATCHER] Sending image message...`);
                await sendFeishuMessage({
                  account,
                  receiveId: channelId,
                  receiveIdType: replyIdType,
                  msgType: "image",
                  content: { image_key: imageKey },
                });
                console.log(`[feishu] [ASYNC] [DISPATCHER] ✓ Image message sent successfully`);
              } catch (imgError) {
                console.error(`[feishu] [ASYNC] [DISPATCHER] ✗ Failed to send image:`, imgError);
                // Fall through to send text message instead
              }
            }
          }

          // Send text message along with images
          if (text) {
            await sendFeishuMessage({
              account,
              receiveId: channelId,
              receiveIdType: replyIdType,
              msgType: "text",
              content: { text },
            });
            console.log(`[feishu] [ASYNC] [DISPATCHER] ✓ Text message sent successfully`);
          }
        } else {
          // No media - just send text
          console.log(`[feishu] [ASYNC] [DISPATCHER] Sending final reply: ${text.substring(0, 100)}...`);

          // Remove typing indicator before sending final reply
          if (typingReactionId) {
            try {
              await removeReaction({
                account,
                messageId: originalMessageId,
                reactionId: typingReactionId,
              });
              console.log(`[feishu] [ASYNC] [DISPATCHER] ✓ Typing indicator removed`);
              typingReactionId = null;
            } catch (removeError) {
              console.error(`[feishu] [ASYNC] [DISPATCHER] ✗ Failed to remove typing indicator:`, removeError);
            }
          }

          // Determine message type based on text length
          // Use card (interactive) for long messages to support Markdown
          const TEXT_THRESHOLD = 200; // Use card for messages longer than 200 chars
          const useCard = text.length > TEXT_THRESHOLD;

          if (useCard) {
            console.log(`[feishu] [ASYNC] [DISPATCHER] Using card format (text length: ${text.length} chars)`);

            // Create card with markdown text
            const card = {
              header: {
                title: "Moltbot 回复",
                template: "blue",
              },
              elements: [
                {
                  tag: "div",
                  text: {
                    tag: "lark_md",
                    content: text,
                  },
                },
              ],
            };

            await sendFeishuMessage({
              account,
              receiveId: channelId,
              receiveIdType: replyIdType,
              msgType: "interactive",
              content: { card: card },
            });
          } else {
            // Short message - use plain text
            await sendFeishuMessage({
              account,
              receiveId: channelId,
              receiveIdType: replyIdType,
              msgType: "text",
              content: { text },
            });
          }
          console.log(`[feishu] [ASYNC] [DISPATCHER] ✓ Final reply sent successfully (${useCard ? 'card' : 'text'})`);
        }

        return true;
      } catch (error) {
        console.error(`[feishu] [ASYNC] [DISPATCHER] ✗ Failed to send final reply:`, error);
        console.error(`[feishu] [ASYNC] [DISPATCHER] Error stack:`, error.stack);
        return false;
      } finally {
        // Signal that processing is complete
        if (resolveProcessing) {
          console.log(`[feishu] [ASYNC] [DISPATCHER] Signaling processing complete`);
          resolveProcessing();
        }
      }
    },
    waitForIdle: async () => {
      console.log(`[feishu] [ASYNC] [DISPATCHER] waitForIdle called - waiting for processing...`);
      // If processingComplete is still pending after a long delay, resolve it ourselves.
      // This handles the case where agent returns NO_REPLY (no sendFinalReply call).
      // Give agent enough time to process (30 seconds) before giving up.
      const fallbackTimeout = setTimeout(() => {
        if (resolveProcessing) {
          console.log(`[feishu] [ASYNC] [DISPATCHER] No reply received after 30s, signaling processing complete (NO_REPLY or timeout?)`);
          // Remove typing indicator on timeout
          if (typingReactionId) {
            removeReaction({
              account,
              messageId: originalMessageId,
              reactionId: typingReactionId,
            }).catch((e) => console.error(`[feishu] Failed to remove typing indicator on timeout:`, e));
            typingReactionId = null;
          }
          resolveProcessing();
        }
      }, 30000); // 30 second fallback for NO_REPLY/timeout case
      await processingComplete;
      clearTimeout(fallbackTimeout);
      console.log(`[feishu] [ASYNC] [DISPATCHER] waitForIdle - processing complete`);
    },
    getQueuedCounts: () => {
      return { tool: 0, block: 0, final: 0 };
    },
  };
  console.log(`[feishu] [ASYNC] [4/6] Dispatcher created successfully`);
  console.log(`[feishu] [ASYNC] [4/6] Dispatcher keys:`, Object.keys(dispatcher));

  // Dispatch message for processing
  console.log(`[feishu] [ASYNC] [5/6] Dispatching message to agent...`);
  console.log(`[feishu] [ASYNC] [CTX] Body="${msgContent?.text}"`);
  console.log(`[feishu] [ASYNC] [CTX] From="${senderId}"`);
  console.log(`[feishu] [ASYNC] [CTX] To="${channelId}"`);
  console.log(`[feishu] [ASYNC] [CTX] AccountId="${accountId}"`);
  console.log(`[feishu] [ASYNC] [CFG] Primary model:`, freshConfig.agents?.defaults?.model?.primary);
  console.log(`[feishu] [ASYNC] [CFG] Auth profiles:`, Object.keys(freshConfig.auth?.profiles || {}));

  try {
    console.log(`[feishu] [ASYNC] [5/6] Calling dispatchInboundMessage (async)...`);
    const result = await dispatchInboundMessage({
      ctx: {
        Body: msgContent?.text || "",
        From: senderId || "",
        AccountId: accountId,
        To: channelId,
        MessageSid: message?.message_id,
        MessageSidFull: message?.message_id,
        // Critical: Provider/Surface identifies the channel for logging and routing
        Provider: "feishu",
        Surface: "feishu",
        // OriginatingChannel tells Moltbot to route replies back to feishu
        OriginatingChannel: "feishu",
        OriginatingTo: channelId,
        // Include provider-specific fields
        channelType: "feishu",
        channelId,
        rawMessage: event,
        metadata: {
          chatType: message?.chat_type,
          messageId: message?.message_id,
          senderName: senderName,
        },
      },
      cfg: freshConfig,
      dispatcher,
    });
    console.log(`[feishu] [ASYNC] [5/6] Dispatch result:`, result);
  } catch (error) {
    console.error(`[feishu] [ASYNC] [ERROR] Dispatch failed:`, error);
    console.error(`[feishu] [ASYNC] [ERROR] Error stack:`, error.stack);
  } finally {
    // Ensure processingComplete is resolved even if no reply was sent (e.g., NO_REPLY)
    if (resolveProcessing) {
      console.log(`[feishu] [ASYNC] Signaling processing complete (dispatch finished)`);
      resolveProcessing();
    }
  }

  console.log(`[feishu] ============================================`);
  console.log(`[feishu] [ASYNC] Background message processing complete`);
  console.log(`[feishu] ============================================`);
}

const plugin = {
  id: "feishu",
  name: "Feishu",
  description: "Moltbot Feishu/Lark channel plugin",
  configSchema: emptyPluginConfigSchema(),
  register(api: MoltbotPluginApi) {
    // Load persisted cache from disk on startup
    loadCacheFromDisk();
    startCacheCleanup();

    // Save cache on process exit
    process.on("exit", () => {
      saveCacheToDisk();
    });
    process.on("SIGINT", () => {
      saveCacheToDisk();
      process.exit(0);
    });
    process.on("SIGTERM", () => {
      saveCacheToDisk();
      process.exit(0);
    });

    // Register channel
    api.registerChannel({ plugin: feishuPlugin, dock: feishuDock });

    // Get webhook path (need to resolve account to get webhook path)
    const initialAccount = resolveFeishuAccount({ cfg: api.runtime.config as any });
    const webhookPath = resolveFeishuWebhookPath(initialAccount);

    // Register HTTP handler for webhooks (Node.js req, res)
    api.registerHttpHandler(async (req: any, res: any): Promise<boolean> => {
      try {
        // Get pathname from request URL
        const urlStr = req.url || "/";
        const pathname = urlStr.split("?")[0]; // Remove query string

        // Check if path matches webhook
        if (pathname === webhookPath && req.method === "POST") {
          console.log(`[feishu] Received webhook request on ${pathname}`);

          let body = "";

          // Collect request body
          await new Promise<void>((resolve, reject) => {
            req.on("data", (chunk: any) => {
              body += chunk.toString();
            });
            req.on("end", () => resolve());
            req.on("error", reject);
          });

          console.log(`[feishu] Request body:`, body.substring(0, 500));

          // Log full event for debugging
          try {
            const data = JSON.parse(body || "{}");
            console.log(`[feishu] [DEBUG] Full event structure:`, JSON.stringify(data, null, 2));
            if (data.event) {
              console.log(`[feishu] [DEBUG] Sender:`, JSON.stringify(data.event.sender, null, 2));
              console.log(`[feishu] [DEBUG] Message:`, JSON.stringify(data.event.message, null, 2));
            }
          } catch (e) {
            // Ignore parse errors
          }

          const data = JSON.parse(body || "{}");

          // Handle URL verification (for initial webhook setup)
          if (data.challenge) {
            console.log(`[feishu] URL verification challenge received`);
            res.statusCode = 200;
            res.setHeader("Content-Type", "application/json; charset=utf-8");
            res.end(JSON.stringify({ challenge: data.challenge }));
            return true;
          }

          // Process message events directly here
          if (data.header?.event_type === "im.message.receive_v1") {
            const messageId = data.event?.message?.message_id;

            // Deduplication: check if we've already processed this message
            if (messageId && messageCache.has(messageId)) {
              console.log(`[feishu] [DEDUP] Duplicate message detected, skipping: ${messageId}`);
              res.statusCode = 200;
              res.setHeader("Content-Type", "application/json; charset=utf-8");
              res.end(JSON.stringify({ code: 0, msg: "success (duplicate)" }));
              return true;
            }

            // Add to cache IMMEDIATELY to prevent duplicates
            if (messageId) {
              messageCache.set(messageId, Date.now());
              console.log(`[feishu] [DEDUP] New message cached: ${messageId} (cache size: ${messageCache.size})`);
              // Save cache to disk every 10 messages to reduce I/O
              if (messageCache.size % 10 === 0) {
                saveCacheToDisk();
              }
            }

            // CRITICAL: Send 200 response IMMEDIATELY before async processing
            // This prevents Feishu from timing out and resending the message
            res.statusCode = 200;
            res.setHeader("Content-Type", "application/json; charset=utf-8");
            res.end(JSON.stringify({ code: 0, msg: "success" }));
            console.log(`[feishu] [ASYNC] Response sent immediately, processing message in background...`);

            // Process message asynchronously (don't await)
            processFeishuMessageAsync(data).catch((error) => {
              console.error(`[feishu] [ASYNC] Error processing message:`, error);
              console.error(`[feishu] [ASYNC] Error stack:`, error.stack);
            });

            return true; // Handled
          }

          return false; // Not handled, let other handlers process
        }
      } catch (error: any) {
        console.error("[feishu] Webhook error:", error);
        res.statusCode = 500;
        res.setHeader("Content-Type", "application/json; charset=utf-8");
        res.end(JSON.stringify({ code: 500, msg: "Internal server error" }));
        return true; // Handled (with error)
      }
    });
  },
};

export default plugin;
