#!/usr/bin/env node
// Test script for Feishu image upload and send

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

async function uploadImage(imageBuffer) {
  console.log("=== Step 1: Uploading Image ===\n");

  const token = await getTenantAccessToken();
  console.log(`✓ Token obtained\n`);

  console.log("Image info:");
  console.log(`  Size: ${imageBuffer.length} bytes`);
  console.log(`  Type: message\n`);

  const formData = new FormData();
  formData.append("image_type", "message");
  formData.append("image", new Blob([imageBuffer]), "screenshot.png");

  console.log("Uploading to /im/v1/images...");

  const response = await fetch("https://open.feishu.cn/open-apis/im/v1/images", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  const data = await response.json();

  console.log(`\n=== Upload Response ===`);
  console.log(`Code: ${data.code}`);
  console.log(`Msg: ${data.msg}`);

  if (data.code !== 0 || !data.data?.image_key) {
    console.error(`\n❌ Upload failed!`);
    console.error(`Full response:`, JSON.stringify(data, null, 2));
    throw new Error(`Upload failed: ${data.msg}`);
  }

  const imageKey = data.data.image_key;
  console.log(`\n✅ SUCCESS! Image uploaded!`);
  console.log(`Image Key: ${imageKey}\n`);

  return imageKey;
}

async function sendImageMessage(imageKey) {
  console.log("=== Step 2: Sending Image Message ===\n");

  const token = await getTenantAccessToken();

  const requestBody = {
    receive_id: OPEN_ID,
    open_id: OPEN_ID,  // Add explicit open_id field
    msg_type: "image",
    content: { image_key: imageKey },
    uuid: crypto.randomUUID(),
  };

  console.log("Sending message:");
  console.log(`  receive_id: ${OPEN_ID}`);
  console.log(`  msg_type: image`);
  console.log(`  content.image_key: ${imageKey.substring(0, 20)}...`);
  console.log(`  Full body: ${JSON.stringify(requestBody, null, 2)}\n`);

  const response = await fetch("https://open.feishu.cn/open-apis/message/v4/send?receive_id_type=open_id", {
    method: "POST",
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify(requestBody),
  });

  const data = await response.json();

  console.log(`=== Send Response ===`);
  console.log(`Code: ${data.code}`);
  console.log(`Msg: ${data.msg}`);

  if (data.code === 0) {
    console.log(`\n✅ SUCCESS! Image message sent!`);
    console.log(`Message ID: ${data.data?.msg_id || "N/A"}`);
  } else {
    console.error(`\n❌ Send failed!`);
    console.error(`Full response:`, JSON.stringify(data, null, 2));
  }
}

async function main() {
  console.log("=== Feishu Image Upload & Send Test ===\n");

  // Read the latest screenshot
  const fs = await import('fs');
  const screenshotFiles = [
    "/tmp/screenshot2.png",
    "/tmp/screenshot.png"
  ];

  let screenshotPath = screenshotFiles.find(path => {
    try {
      return fs.existsSync(path);
    } catch {
      return false;
    }
  });

  if (!screenshotPath) {
    console.error("❌ No screenshot file found!");
    console.log("Looking for:", screenshotFiles.join(", "));
    return;
  }

  console.log(`Found screenshot: ${screenshotPath}`);
  const imageBuffer = fs.readFileSync(screenshotPath);
  console.log(`Read ${imageBuffer.length} bytes\n`);

  try {
    const imageKey = await uploadImage(imageBuffer);
    await sendImageMessage(imageKey);
  } catch (error) {
    console.error("\n❌ Error:", error.message);
    console.error(error.stack);
  }
}

main().catch(console.error);
