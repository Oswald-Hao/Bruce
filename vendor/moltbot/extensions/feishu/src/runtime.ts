import type { FeishuRuntimeState, FeishuMonitor } from "./types.config.js";

// Global runtime state
const runtimeState: FeishuRuntimeState = {
  monitors: new Map(),
};

/**
 * Get Feishu runtime state
 */
export const getFeishuRuntimeState = (): FeishuRuntimeState => {
  return runtimeState;
};

/**
 * Get Feishu monitor for account
 */
export const getFeishuMonitor = (accountId: string): FeishuMonitor | undefined => {
  return runtimeState.monitors.get(accountId);
};

/**
 * Set Feishu monitor for account
 */
export const setFeishuMonitor = (accountId: string, monitor: FeishuMonitor): void => {
  runtimeState.monitors.set(accountId, monitor);
};

/**
 * Remove Feishu monitor for account
 */
export const removeFeishuMonitor = (accountId: string): void => {
  const monitor = runtimeState.monitors.get(accountId);
  if (monitor?.server) {
    // Close server if exists
    try {
      monitor.server.close();
    } catch (error) {
      console.error(`Failed to close Feishu monitor server for ${accountId}:`, error);
    }
  }
  runtimeState.monitors.delete(accountId);
};

/**
 * Get all monitor account IDs
 */
export const getFeishuMonitorAccountIds = (): string[] => {
  return Array.from(runtimeState.monitors.keys());
};
