import gradio as gr
from chat import chat
from search import search

# 存储聊天记录（OpenAI格式）
messages = []

def add_text(history, text):
    """
    处理用户输入文本（支持/search指令）
    """
    global messages
    
    # 添加到界面历史记录（显示原始内容）
    history = history + [{"role": "user", "content": text}]
    
    # 处理搜索指令
    if text.startswith("/search "):
        search_content = text[8:].strip()
        processed_content = search(search_content)
        messages.append({"role": "user", "content": processed_content})
    else:
        messages.append({"role": "user", "content": text})
    
    return history, gr.update(value="", interactive=False)

def bot(history):
    """
    生成AI助手的回复（流式传输）
    """
    global messages
    
    try:
        # 获取流式响应生成器
        response_generator = chat(messages)
        
        # 初始化回复内容
        response = ""
        
        # 创建新历史记录，保留之前的所有记录
        new_history = history.copy()
        
        # 添加等待回复的状态
        new_history.append({"role": "assistant", "content": ""})
        
        # 逐步获取流式响应
        for chunk in response_generator:
            response += chunk
            # 更新最后一条助手的回复
            new_history[-1] = {"role": "assistant", "content": response}
            yield new_history
        
        # 更新完整聊天记录
        messages.append({"role": "assistant", "content": response})
        
    except Exception as e:
        error_msg = f"⚠️ error: {str(e)}"
        # 添加错误消息
        if history:
            new_history = history.copy()
        else:
            new_history = []
        new_history.append({"role": "assistant", "content": error_msg})
        yield new_history

def clear_chat():
    """
    清除聊天记录
    """
    global messages
    messages = []
    return []

with gr.Blocks() as demo:
    # 使用新格式的Chatbot组件
    chatbot = gr.Chatbot([], 
                        elem_id="chatbot", 
                        label="AI助手", 
                        type="messages")  # 关键修改
    
    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="输入消息或指令（如/search 内容）",
            container=False,
        )
        clear_btn = gr.Button('清除')

    # 文本提交处理
    txt_msg = txt.submit(
        add_text, 
        [chatbot, txt], 
        [chatbot, txt], 
        queue=False
    ).then(
        bot, 
        chatbot, 
        chatbot
    )
    
    txt_msg.then(
        lambda: gr.update(interactive=True), 
        None, 
        [txt], 
        queue=False
    )
    
    # 清除聊天记录
    clear_btn.click(
        clear_chat, 
        None, 
        chatbot, 
        queue=False
    )

# 添加详细的启动配置
if __name__ == "__main__":
    demo.queue()
    demo.launch(
        server_name="0.0.0.0", 
        server_port=7860,
        debug=True,  # 启用调试模式
        show_error=True  # 显示详细错误
    )