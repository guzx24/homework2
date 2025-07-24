import requests
import os

def chat(messages):
    """
    调用 LocalAI 的聊天接口并返回助手回复
    """
    # LocalAI 的 API 配置（根据文档 https://localai.io/docs/overview/）
    LOCALAI_API_URL = "http://localhost:8080/v1/chat/completions"
    MODEL_NAME = "gpt-3.5-turbo"  # 替换为实际使用的模型名
    
    try:
        # 构建 API 请求
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": 0.7
        }
        
        # 发送请求
        response = requests.post(
            LOCALAI_API_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=600  # 60秒超时
        )
        
        # 处理响应
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"⚠️ API error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"⚠️ request failed: {str(e)}"