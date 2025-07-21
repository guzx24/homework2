import requests
import json
import logging
import time

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def chat(messages, max_retries=3, retry_delay=2):
    """
    调用 LocalAI 的聊天接口并返回助手回复（流式传输）
    """
    LOCALAI_API_URL = "http://localhost:8080/v1/chat/completions"
    MODEL_NAME = "gpt-3.5-turbo"
    
    for attempt in range(max_retries):
        try:
            # 构建流式请求
            payload = {
                "model": MODEL_NAME,
                "messages": messages,
                "temperature": 0.7,
                "stream": True
            }
            
            logger.info(f"发送请求到LocalAI (尝试 {attempt+1}/{max_retries})")
            
            # 发送流式请求
            response = requests.post(
                LOCALAI_API_URL,
                headers={"Content-Type": "application/json"},
                json=payload,
                stream=True,
                timeout=30
            )
            
            # 检查响应状态
            if response.status_code == 200:
                # 处理流式响应
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8').strip()
                        if decoded_line.startswith("data: "):
                            data = decoded_line[6:]
                            if data == "[DONE]":
                                return
                            
                            try:
                                chunk_data = json.loads(data)
                                if 'choices' in chunk_data and chunk_data['choices']:
                                    delta = chunk_data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
                return  # 成功完成，退出函数
            
            # 处理错误状态码
            error_msg = f"API错误: {response.status_code} - {response.text}"
            logger.error(error_msg)
            yield f"⚠️ {error_msg}"
            return
            
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                logger.warning(f"连接失败，{retry_delay}秒后重试...")
                time.sleep(retry_delay)
                continue
            else:
                error_msg = "⚠️ 无法连接到LocalAI服务，请确保服务已启动: `docker compose up -d`"
                logger.error(error_msg)
                yield error_msg
                return
                
        except requests.exceptions.Timeout:
            error_msg = "⚠️ 请求超时，请稍后再试"
            logger.error(error_msg)
            yield error_msg
            return
            
        except Exception as e:
            error_msg = f"⚠️ 请求失败: {str(e)}"
            logger.error(error_msg)
            yield error_msg
            return

    error_msg = f"⚠️ 经过 {max_retries} 次重试后仍失败"
    logger.error(error_msg)
    yield error_msg