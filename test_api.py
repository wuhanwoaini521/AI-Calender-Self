#!/usr/bin/env python3
"""
测试脚本 - 测试 Calendar MCP Backend 的各个功能
"""

import requests
import json
from datetime import datetime, timedelta

# API 基础 URL
BASE_URL = "https://api.moonshot.cn/v1"

# 你的 Anthropic API Key（测试用）
API_KEY = "sk-kimi-bGmbnpqS9eMZIQLTbP1YSEYREoXcbNCXMm8XZfHR022UKXK8eIWtC2mmlhFm3MA8"  # 替换为你的 API Key

# 请求头
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY  # 添加 API Key 到请求头
}


def print_response(title, response):
    """打印响应"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_chat_create_event():
    """测试通过对话创建事件"""
    url = f"{BASE_URL}/chat"
    
    data = {
        "message": "帮我添加一个明天下午3点的团队会议，地点在会议室A",
        "conversation_history": []
    }
    
    response = requests.post(url, json=data, headers=HEADERS)
    print_response("测试 1: 通过对话创建事件", response)
    return response


def test_chat_list_events():
    """测试通过对话查询事件"""
    url = f"{BASE_URL}/chat"
    
    data = {
        "message": "显示所有的日程安排",
        "conversation_history": []
    }
    
    response = requests.post(url, json=data, headers=HEADERS)
    print_response("测试 2: 通过对话查询事件", response)
    return response


def test_without_api_key():
    """测试没有 API Key 的请求"""
    url = f"{BASE_URL}/chat"
    
    data = {
        "message": "测试",
        "conversation_history": []
    }
    
    # 不传 API Key
    response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
    print_response("测试: 不传 API Key（应该返回 401）", response)
    return response


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("Calendar MCP Backend 测试")
    print("="*60)
    
    if API_KEY == "sk-ant-xxxxx":
        print("\n⚠️  警告: 请先在脚本中设置你的 API_KEY")
        print("修改 test_api.py 中的 API_KEY 变量\n")
        return
    
    try:
        # 检查服务是否运行
        response = requests.get("http://localhost:8000/health")
        if response.status_code != 200:
            print("错误: 服务未运行，请先启动服务")
            return
        
        print("\n✓ 服务运行正常\n")
        
        # 运行测试
        test_without_api_key()
        test_chat_create_event()
        test_chat_list_events()
        
        print("\n" + "="*60)
        print("所有测试完成！")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n错误: 无法连接到服务")
        print("请确保服务正在运行: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n错误: {str(e)}")


if __name__ == "__main__":
    main()