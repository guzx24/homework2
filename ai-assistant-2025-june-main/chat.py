# import os
# from openai import OpenAI

# # 配置本地LocalAI API
# client = OpenAI(
#     base_url="http://localhost:8080/v1",  # LocalAI的API地址
#     api_key="a94695382f364300dd39e0d91aba0d5f39d4358b628309d4cf91ad0ca183ec63"  # 任意非空字符串
# )

# def chat(messages):
#     """
#     调用语言模型进行流式聊天回复
#     :param messages: 聊天记录列表
#     :return: 流式传输的生成器
#     """
#     try:
#         # 调用本地语言模型（仅流式传输）
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",  # 使用配置的模型
#             messages=messages,
#             stream=True,  # 强制使用流式输出
#             temperature=0.7
#         )
        
#         # 流式传输生成器
#         full_response = ""
#         for chunk in response:
#             if chunk.choices[0].delta.content:
#                 content = chunk.choices[0].delta.content
#                 full_response += content
#                 yield content
        
#         # 将完整回复添加到消息记录
#         messages.append({"role": "assistant", "content": full_response})
            
#     except Exception as e:
#         print(f"API调用错误: {e}")
#         yield "抱歉，我遇到了问题，暂时无法回答。"

# # import requests
# import json

# def chat(messages):
#     """
#     使用 requests 库直接调用 LocalAI 的流式 API，以确保 UTF-8 编码被正确处理。
#     """
#     # LocalAI 的 API 地址
#     url = "http://localhost:8080/v1/chat/completions"
    
#     # 请求头
#     headers = {
#         "Content-Type": "application/json"
#     }
    
#     # 请求体
#     payload = {
#         "model": "gpt-3.5-turbo",
#         "messages": messages,
#         "stream": True,
#         "temperature": 0.7
#     }

#     try:
#         # 发送 POST 请求，并开启流式接收
#         with requests.post(url, headers=headers, json=payload, stream=True) as response:
#             # 检查请求是否成功
#             response.raise_for_status()
            
#             # 逐行读取流式响应
#             for line in response.iter_lines():
#                 # 必须将收到的字节流解码为 UTF-8 字符串
#                 decoded_line = line.decode('utf-8')
                
#                 # SSE (Server-Sent Events) 格式以 "data: " 开头
#                 if decoded_line.startswith('data: '):
#                     # 去掉 "data: " 前缀
#                     json_str = decoded_line[6:]
                    
#                     # 有时候会收到一个表示流结束的 [DONE] 标记
#                     if json_str.strip() == "[DONE]":
#                         continue
                        
#                     try:
#                         # 解析 JSON 字符串
#                         data = json.loads(json_str)
                        
#                         # 提取内容
#                         if data['choices'][0]['delta'] and 'content' in data['choices'][0]['delta']:
#                             content = data['choices'][0]['delta']['content']
#                             if content:
#                                 yield content
#                     except json.JSONDecodeError:
#                         # 忽略无法解析的行
#                         continue

#     except requests.exceptions.RequestException as e:
#         print(f"--- [chat.py] 网络请求错误: {e} ---")
#         yield "抱歉，连接 AI 服务时出现网络问题。"
#     except Exception as e:
#         print(f"--- [chat.py] 处理数据流时发生未知错误: {e} ---")
#         yield "抱歉，处理 AI 回复时发生未知错误。"


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