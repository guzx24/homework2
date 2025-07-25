

import requests
import json

def chat(messages, keep_history=False):
    """
    使用 requests 库直接调用 LocalAI 的流式 API，以确保 UTF-8 编码被正确处理。
    :param messages: List of message dictionaries
    :param keep_history: If False, only use the latest user message
    """
    # LocalAI 的 API 地址
    url = "http://localhost:8080/v1/chat/completions"
    
    # 请求头
    headers = {
        "Content-Type": "application/json"
    }
    
    # If keep_history is False, only use the last user message
    if not keep_history:
        messages = [msg for msg in messages if msg["role"] == "user"][-1:]
    
    # 请求体
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "stream": True,
        "temperature": 0.7
    }

    try:
        # 发送 POST 请求，并开启流式接收
        with requests.post(url, headers=headers, json=payload, stream=True) as response:
            response.raise_for_status()
            
            for line in response.iter_lines():
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    json_str = decoded_line[6:]
                    if json_str.strip() == "[DONE]":
                        continue
                    try:
                        data = json.loads(json_str)
                        if data['choices'][0]['delta'] and 'content' in data['choices'][0]['delta']:
                            content = data['choices'][0]['delta']['content']
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue

    except requests.exceptions.RequestException as e:
        print(f"--- [chat.py] 网络请求错误: {e} ---")
        yield "抱歉，连接 AI 服务时出现网络问题。"
    except Exception as e:
        print(f"--- [chat.py] 处理数据流时发生未知错误: {e} ---")
        yield "抱歉，处理 AI 回复时发生未知错误。"