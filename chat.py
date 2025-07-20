import openai

# 设置 LocalAI 的 API 地址
openai.api_base = "http://localhost:8080/v1"  # 关键设置！
openai.api_key = "sk-any-key"  # 任意非空字符串（LocalAI 不需要真实密钥）

def chat(messages):
    """
    使用流式传输与语言模型交互
    """
    try:
        # 调用 LocalAI 的 GPT-3.5 模型
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 必须与 LocalAI 中的模型 ID 匹配
            messages=messages,
            stream=True,
            temperature=0.7
        )
        
        # 处理流式响应
        for chunk in response:
            if hasattr(chunk.choices[0].delta, "content"):
                content = chunk.choices[0].delta.content
                if content is not None:
                    yield content
    
    except Exception as e:
        # 错误处理
        error_msg = f"⚠️ API 错误: {str(e)}"
        yield error_msg