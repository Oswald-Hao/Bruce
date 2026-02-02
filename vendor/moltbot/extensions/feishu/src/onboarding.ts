import {
  text,
  confirm,
  select,
  type PromptOptions,
} from "@clack/prompts";
import { getChannelValueWithAccount } from "clawdbot/plugin-sdk";
import type { MoltbotConfig, ChannelOnboardingAdapter } from "clawdbot/plugin-sdk";
import { validateFeishuCredentials, maskAppSecret } from "./auth.js";
import type { ResolvedFeishuAccount, FeishuConfig } from "./types.config.js";
import { resolveFeishuAccount } from "./accounts.js";
import { probeFeishu } from "./api.js";

/**
 * Onboarding adapter for Feishu channel
 */
export const feishuOnboardingAdapter: ChannelOnboardingAdapter = {
  id: "feishu",
  prompt: async ({ cfg, accountId = "default" }) => {
    const account = resolveFeishuAccount({ cfg: cfg as MoltbotConfig, accountId });

    console.log("");
    console.log("Feishu/Lark Bot Setup");
    console.log("--------------------");
    console.log(
      "To set up a Feishu bot, you'll need:"
    );
    console.log("");
    console.log("1. Go to https://open.feishu.cn/app");
    console.log("2. Create a new app or select an existing one");
    console.log("3. Get your App ID and App Secret from the app credentials page");
    console.log("4. Enable 'Events' and configure webhook URL");
    console.log("5. Request permissions: im:message, im:message:send_as_bot");
    console.log("");

    const shouldContinue = await confirm({
      message: "Have you created a Feishu app?",
      initialValue: false,
    });

    if (typeof shouldContinue !== "boolean" || !shouldContinue) {
      throw new Error("Feishu app is required. Please create one first.");
    }

    // App ID
    const appId = await text({
      message: "Enter your Feishu App ID (e.g., cli_xxxxxxxxxxxxxxxx):",
      placeholder: account.credentialSource !== "none" ? account.config.appId : undefined,
      validate: (value) => {
        if (!value || !value.trim()) {
          return "App ID is required";
        }
        if (!/^cli_[a-zA-Z0-9]{28}$/.test(value.trim())) {
          return "Invalid App ID format (should be cli_ followed by 28 alphanumeric characters)";
        }
      },
    });

    if (typeof appId !== "string") {
      throw new Error("App ID is required");
    }

    // App Secret
    const appSecret = await text({
      message: "Enter your Feishu App Secret:",
      placeholder:
        account.credentialSource !== "none"
          ? maskAppSecret(account.config.appSecret)
          : undefined,
      validate: (value) => {
        if (!value || !value.trim()) {
          return "App Secret is required";
        }
        if (value.trim().length < 20) {
          return "App Secret is too short (should be at least 20 characters)";
        }
      },
    });

    if (typeof appSecret !== "string") {
      throw new Error("App Secret is required");
    }

    // Verify Token (optional, for webhook verification)
    const verifyToken = await text({
      message: "Enter your Verify Token (optional, for webhook verification):",
      placeholder: account.config.webhookPath || "",
    });

    // Encrypt Key (optional, for webhook encryption)
    const encryptKey = await text({
      message: "Enter your Encrypt Key (optional, for webhook encryption):",
      placeholder: "",
    });

    // Webhook URL
    const webhookUrl = await text({
      message: "Enter your webhook URL (optional, leave empty for auto-configuration):",
      placeholder: account.config.webhookUrl || "",
    });

    // Webhook path
    const webhookPath = await text({
      message: "Enter webhook path (default: /feishu/default):",
      placeholder: account.config.webhookPath || "/feishu/default",
    });

    // Test credentials
    const shouldTest = await confirm({
      message: "Test credentials now?",
      initialValue: true,
    });

    if (shouldTest === true) {
      console.log("");
      console.log("Testing Feishu connection...");

      const testAccount: ResolvedFeishuAccount = {
        accountId,
        name: account.name,
        enabled: true,
        credentialSource: "config",
        config: {
          appId: appId.trim(),
          appSecret: appSecret.trim(),
          appType: "self_build",
          webhookPath: webhookPath?.trim() || "/feishu/default",
          webhookUrl: webhookUrl?.trim(),
        },
      };

      const isValid = await probeFeishu({ account: testAccount });

      if (!isValid) {
        const shouldContinue = await confirm({
          message: "Connection test failed. Continue anyway?",
          initialValue: false,
        });

        if (shouldContinue !== true) {
          throw new Error("Feishu connection test failed");
        }
      } else {
        console.log("✓ Feishu connection successful!");
      }
    }

    console.log("");
    console.log("Feishu bot configuration complete!");
    console.log("");
    console.log("Next steps:");
    console.log("1. Configure your webhook URL in Feishu app:");
    console.log(
      `   https://your-domain.com${webhookPath?.trim() || "/feishu/default"}`
    );
    console.log("2. Enable events: im.message.receive_v1");
    console.log("3. Add permissions: im:message, im:message:send_as_bot");
    console.log("");

    return {
      accountId,
      config: {
        appId: appId.trim(),
        appSecret: appSecret.trim(),
        verifyToken: verifyToken?.trim(),
        encryptKey: encryptKey?.trim(),
        webhookPath: webhookPath?.trim() || "/feishu/default",
        webhookUrl: webhookUrl?.trim(),
      },
    };
  },
};
