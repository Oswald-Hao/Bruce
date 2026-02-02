#!/usr/bin/env node
// Test script following Node.js SDK pattern
// Based on: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/nodejs-sdk/preparation-before-development

const APP_ID = "cli_a9f05a5e0378dcb0";
const APP_SECRET = "KdosR8d6vhlLdM6yP9nrUdSwb2VoevJr";
const RECEIVE_ID = "oc_d130fd4a7085e4cf5f313f27d3e180bd";
const TENANT_TOKEN = "t-g1041tjP63RE55E7GSZH6CRXVRNRO7VPUKKZX6JU";

async function sendMessage() {
  console.log("=== Feishu Send Message Test (Node.js SDK Pattern) ===\n");

  console.log("Step 1: Creating message request (Node.js SDK pattern)...");
  console.log(`  params.receive_id_type: "chat_id"`);
  console.log(`  data.receive_id: ${RECEIVE_ID}`);
  console.log(`  data.msg_type: "text"`);
  console.log(`  data.content: '{"text":"test content"}' (JSON string)`);
  console.log(`  data.uuid: "选填，每次调用前请更换，如a0d69e20-1dd1-458b-k525-dfeca4015204"`);
  console.log(`  withTenantToken: ${TENANT_TOKEN}\n`);

  // Node.js SDK pattern:
  // - receive_id_type goes in params (URL query params)
  // - receive_id, msg_type, content, uuid go in data (body)
  // - content is JSON string (exactly as shown)
  // - tenant_access_token passed via Authorization header (or withTenantToken in SDK)

  const requestBody = {
    receive_id: RECEIVE_ID,
    chat_id: RECEIVE_ID,  // Add explicit chat_id field
    msg_type: "text",
    content: { text: "test content" },  // Try object instead of JSON string
    uuid: "选填，每次调用前请更换，如a0d69e20-1dd1-458b-k525-dfeca4015204",
  };

  console.log("Step 2: Sending to API...");
  console.log(`  URL: /message/v4/send?receive_id_type=chat_id`);
  console.log(`  Method: POST`);
  console.log(`  Headers:`);
  console.log(`    Content-Type: application/json; charset=utf-8`);
  console.log(`    Authorization: Bearer ${TENANT_TOKEN}`);
  console.log(`  Body: ${JSON.stringify(requestBody)}\n`);

  const url = `https://open.feishu.cn/open-apis/message/v4/send?receive_id_type=chat_id`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Authorization": `Bearer ${TENANT_TOKEN}`,
    },
    body: JSON.stringify(requestBody),
  });

  const data = await response.json();

  console.log(`=== Response ===`);
  console.log(`Code: ${data.code}`);
  console.log(`Msg: ${data.msg}`);
  console.log(`Request ID: ${data.request_id || "N/A"}`);

  if (data.code === 0) {
    console.log(`\n✅ SUCCESS! Message sent!`);
    console.log(`Message ID: ${data.data?.msg_id || "N/A"}`);
  } else {
    console.error(`\n❌ FAILED!`);
    console.error(`Full response: ${JSON.stringify(data, null, 2)}`);
  }
}

sendMessage().catch(console.error);
