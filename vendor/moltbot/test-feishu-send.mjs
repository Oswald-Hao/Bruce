#!/usr/bin/env node
// Test script to send message to Feishu

const APP_ID = "cli_a9f05a5e0378dcb0";
const APP_SECRET = "KdosR8d6vhlLdM6yP9nrUdSwb2VoevJr";
const OPEN_ID = "ou_ac30832212aa13310b80594b6a24b8d9"; // Your open_id

async function getTenantAccessToken() {
  const response = await fetch("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal", {
    method: "POST",
    headers: {
      "Content-Type": "application/json; charset=utf-8",
    },
    body: JSON.stringify({
      app_id: APP_ID,
      app_secret: APP_SECRET,
    }),
  });

  const data = await response.json();
  if (data.code !== 0) {
    throw new Error(`Failed to get token: ${data.msg}`);
  }
  return data.tenant_access_token;
}

async function sendMessage() {
  console.log("Getting tenant access token...");
  const token = await getTenantAccessToken();
  console.log("Token obtained");

  console.log("Sending message to Feishu...");
  console.log(`  Open ID: ${OPEN_ID}`);

  const requestBody = {
    msg_type: "text",
    receive_id: OPEN_ID,
    open_id: OPEN_ID,  // Add explicit open_id field
    // Try with object instead of JSON string
    content: { text: "测试消息：你好！这是Moltbot飞书集成测试。" },
    uuid: crypto.randomUUID(),
  };

  console.log(`  Request body: ${JSON.stringify(requestBody)}`);

  // receive_id_type only in URL params (like Java SDK)
  const response = await fetch("https://open.feishu.cn/open-apis/message/v4/send?receive_id_type=open_id", {
    method: "POST",
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Authorization": `Bearer ${token}`,
      // No custom header
    },
    body: JSON.stringify(requestBody),
  });

  const data = await response.json();
  console.log(`\nResponse code: ${data.code}`);
  console.log(`Response msg: ${data.msg}`);

  if (data.code === 0) {
    console.log(`\n✓ Message sent successfully! Message ID: ${data.data?.msg_id}`);
  } else {
    console.error(`\n✗ Failed to send message`);
    console.error(`Full response: ${JSON.stringify(data, null, 2)}`);
  }
}

sendMessage().catch(console.error);
