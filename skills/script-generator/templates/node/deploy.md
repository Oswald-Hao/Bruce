#!/usr/bin/env node
/**
 * Description: 监听指定目录的文件变化，自动执行部署命令
 * 自动生成的Node.js脚本 - 部署脚本
 * 生成时间: {{timestamp}}
 * 需求: {{prompt}
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const chokidar = require('chokidar');

class FileDeployer {
  constructor(sourceDir, targetDir, deployCommand) {
    this.sourceDir = sourceDir;
    this.targetDir = targetDir;
    this.deployCommand = deployCommand;
    this.isDeploying = false;
  }

  log(message, level = 'INFO') {
    const timestamp = new Date().toISOString();
    const logLine = `[${timestamp}] [${level}] ${message}\n`;
    process.stdout.write(logLine);
  }

  async deploy() {
    if (this.isDeploying) {
      this.log('部署中，跳过本次', 'WARNING');
      return;
    }

    this.isDeploying = true;
    this.log('开始部署...');

    try {
      // 执行部署命令
      if (this.deployCommand) {
        this.log(`执行命令: ${this.deployCommand}`);
        execSync(this.deployCommand, { stdio: 'inherit' });
      }

      this.log('部署完成！', 'INFO');
    } catch (error) {
      this.log(`部署失败: ${error.message}`, 'ERROR');
    } finally {
      this.isDeploying = false;
    }
  }

  watch() {
    this.log(`开始监听: ${this.sourceDir}`);

    const watcher = chokidar.watch(this.sourceDir, {
      ignored: /(^|[\/\\])\../,  // 忽略点文件
      persistent: true,
      awaitWriteFinish: {
        stabilityThreshold: 2000,
        pollInterval: 100
      }
    });

    watcher
      .on('add', path => {
        this.log(`文件添加: ${path}`);
        this.deploy();
      })
      .on('change', path => {
        this.log(`文件变更: ${path}`);
        this.deploy();
      })
      .on('unlink', path => {
        this.log(`文件删除: ${path}`);
        this.deploy();
      })
      .on('error', error => {
        this.log(`监听错误: ${error}`, 'ERROR');
      });
  }
}

// 命令行参数
const args = process.argv.slice(2);
const sourceDir = args[0] || './src';
const targetDir = args[1] || '/var/www';
const deployCommand = args[2] || 'npm run build';

const deployer = new FileDeployer(sourceDir, targetDir, deployCommand);

// 检查是否需要安装依赖
try {
  require.resolve('chokidar');
} catch (e) {
  console.log('请先安装依赖: npm install chokidar');
  process.exit(1);
}

// 开始监听
deployer.watch();
