import type { ChannelMessageActionAdapter } from "clawdbot/plugin-sdk";
import type { ResolvedFeishuAccount } from "./types.config.js";
import { sendFeishuMessage } from "./api.js";
import { formatFeishuTarget } from "./targets.js";

/**
 * Feishu message actions
 */
export const feishuMessageActions: ChannelMessageActionAdapter = {
  listActions: () => {
    // Feishu specific actions can be listed here
    return [];
  },

  extractToolSend: () => {
    return null;
  },

  handleAction: async () => {
    throw new Error("Feishu actions are not implemented yet.");
  },
};
