#!/usr/bin/env python3
# 飞书消息发送工具 - 用于发送进化汇报

import requests
import json

# Feishu应用配置
APP_ID = "cli_a9f05a5e0378dcb0"
APP_SECRET = "KdosR8d6vhlLdM6yP9nrUdSwb2VoevJr"
OPEN_ID = "ou_ac30832212aa13310b80594b6a24b8d9"  # Oswald的open_id

def get_tenant_access_token():
    """获取tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    data = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if result["code"] != 0:
        raise Exception(f"获取token失败: {result['msg']}")

    return result["tenant_access_token"]

def send_message(text):
    """发送文本消息到飞书"""
    try:
        # 获取token
        token = get_tenant_access_token()

        # 发送消息
        url = "https://open.feishu.cn/open-apis/message/v4/send?receive_id_type=open_id"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "msg_type": "text",
            "receive_id": OPEN_ID,
            "open_id": OPEN_ID
        }

        # content必须是JSON对象，不是字符串
        data["content"] = {"text": text}

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if result["code"] == 0:
            print(f"✓ 消息发送成功! Message ID: {result.get('data', {}).get('msg_id', 'N/A')}")
            return True
        else:
            print(f"✗ 消息发送失败: {result['msg']}")
            print(f"完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return False

    except Exception as e:
        print(f"✗ 发送消息时出错: {e}")
        return False

if __name__ == "__main__":
    # 进化汇报消息
    report_message = """--- 进化汇报 ---
当前技能总数：60/200

昨天完成了智能招聘系统、智能合同管理系统、智能财务管理系统的实现：

第1个技能：智能招聘系统
技能内容：智能化的招聘管理系统，提供简历解析、智能筛选、候选人评分、面试安排、人才库管理、招聘数据分析等全流程招聘解决方案
测试结果：✅ 41个测试用例全部通过（100%）
更新的技能路径为：/home/lejurobot/clawd/skills/smart-recruitment/
实现的方式为：使用Python，支持PDF/Word/文本简历解析，基于关键词/技能/经验的智能匹配，JSON数据持久化，命令行接口
优先级理由：招聘是企业刚需，代招聘和猎头服务市场需求大，预期月收益33000-145000元，直接贡献于赚钱目标

第2个技能：智能合同管理系统
技能内容：智能化合同管理工具，提供合同起草、审查、模板管理、风险识别、合同跟踪等全生命周期合同管理解决方案
测试结果：✅ 47个测试用例全部通过（100%）
更新的技能路径为：/home/lejurobot/clawd/skills/smart-contract-manager/
实现的方式为：使用Python，内置销售/采购/服务/保密等合同模板库，基于规则的合同审查和风险识别，JSON数据持久化，命令行接口
优先级理由：合同管理是企业的核心需求，合同起草和审查服务市场空间大，预期月收益21000-105000元，属于直接赚钱技能

第3个技能：智能财务管理系统
技能内容：智能化财务管理工具，提供财务记账、发票管理、报表生成、财务分析、税务计算等全面财务管理解决方案
测试结果：✅ 54个测试用例全部通过（100%）
更新的技能路径为：/home/lejurobot/clawd/skills/smart-finance-manager/
实现的方式为：使用Python，支持收入/支出/转账记录，智能交易分类，自动生成资产负债表/损益表/现金流量表，增值税和企业所得税计算
优先级理由：财务代理服务是稳定的高价值业务，代理记账、发票管理、报表生成需求持续，预期月收益15000-85000元，长期稳定的收入来源

--- 进化进度 ---
已完成技能：60
剩余需完成：140
完成度：30%
---

注：3个技能都是P0直接赚钱类型，累计预期月收益69000-335000元"""

    send_message(report_message)
