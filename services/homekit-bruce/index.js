#!/usr/bin/env node

const { Accessory, Service, Characteristic, uuid } = require('hap-nodejs');
const http = require('http');

// Bruce HomeKit Accessory
const BruceAccessory = {
  name: 'Bruce AI Assistant',
  model: 'Bruce-HomeKit-v1',
  pincode: '123-45-678',
  port: 18790,
  username: '1E:49:7C:34:56:A0'
};

// 创建配件
const accessoryUUID = uuid.generate('homekit:bruce:assistant');
const accessory = new Accessory(BruceAccessory.name, accessoryUUID);

// 添加信息服务
accessory
  .getService(Service.AccessoryInformation)
  .setCharacteristic(Characteristic.Manufacturer, 'Bruce AI')
  .setCharacteristic(Characteristic.Model, BruceAccessory.model)
  .setCharacteristic(Characteristic.SerialNumber, 'BRUCE-001')
  .setCharacteristic(Characteristic.FirmwareRevision, '1.0.0');

// 添加Lightbulb服务（AI触发器）
const triggerService = accessory.addService(Service.Lightbulb, 'Bruce AI');

// 电源特征（触发AI）
const powerCharacteristic = triggerService.getCharacteristic(Characteristic.On);

// 添加Name特征（存储问题）
const questionCharacteristic = triggerService.getCharacteristic(Characteristic.Name);

// 初始化
powerCharacteristic.updateValue(false);
questionCharacteristic.updateValue('');

// 调用Moltbot API
async function callMoltbot(question) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'localhost',
      port: 18789,
      path: '/agent',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer qwe748868317'
      },
      timeout: 30000
    };

    const req = http.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          if (res.statusCode === 200) {
            const response = data.trim();
            resolve(response);
          } else {
            reject(`HTTP ${res.statusCode}`);
          }
        } catch (e) {
          resolve(data);
        }
      });
    });

    req.on('error', (e) => {
      reject(`Connection error: ${e.message}`);
    });

    req.on('timeout', () => {
      req.destroy();
      reject('Request timeout');
    });

    req.write(JSON.stringify({ message: question }));
    req.end();
  });
}

// 存储问题
let storedQuestion = '';

// 监听Name变化
questionCharacteristic.on('change', (value) => {
  const question = value.newValue;
  if (question && question.trim() !== '') {
    storedQuestion = question;
    console.log(`[Bruce] Question received: ${question.substring(0, 50)}...`);
  }
});

// 监听电源变化
powerCharacteristic.on('set', (value, callback) => {
  console.log(`[Bruce] Trigger: ${value}`);

  if (value && storedQuestion && storedQuestion.trim() !== '') {
    console.log(`[Bruce] Processing question...`);

    // 调用Moltbot
    callMoltbot(storedQuestion)
      .then(response => {
        console.log(`[Bruce] Response: ${response.substring(0, 80)}...`);
        // 更新Name为回复
        questionCharacteristic.updateValue(`✓ ${response.substring(0, 200)}`);
      })
      .catch(error => {
        console.error(`[Bruce] Error: ${error}`);
        questionCharacteristic.updateValue(`Error: ${error.substring(0, 50)}`);
      });
  }

  callback();
});

// Identify
accessory.on('identify', (paired, callback) => {
  console.log('[Bruce] Identify requested');
  callback();
});

// 发布配件
accessory.publish({
  username: BruceAccessory.username,
  port: BruceAccessory.port,
  pincode: BruceAccessory.pincode,
  category: Accessory.Categories.SPEAKER,
}, () => {
  console.log('[Bruce] HomeKit accessory published!');
  console.log(`[Bruce] PIN: ${BruceAccessory.pincode}`);
  console.log(`[Bruce] Name: ${BruceAccessory.name}`);
  console.log('[Bruce] Ready for Siri integration');
});

// 优雅关闭
process.on('SIGINT', () => {
  console.log('\n[Bruce] Shutting down...');
  accessory.unpublish();
  process.exit(0);
});
