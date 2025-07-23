import gradio as gr
import os
import time
from chat import chat
from search import search

# 初始化变量
messages = []  # 完整聊天记录: [{"role": "user", "content": ...}, ...]
history = []   # 界面显示记录: [{"role": "user", "content": ...}, ...]
current_file_text = None

def add_text(history_state, text):
    """
    处理用户文本输入
    """
    global messages
    
    # 检查是否是特殊指令
    if text.startswith('/search'):
        # 处理搜索指令
        query = text[8:].strip()
        processed_content = search(query)
        
        # 添加到消息记录
        messages.append({"role": "user", "content": processed_content})
        
        # 界面显示原始指令
        new_history = history_state + [{"role": "user", "content": f"/search {query}"}]
        return new_history, gr.update(value="", interactive=False)
    
    # 普通消息
    messages.append({"role": "user", "content": text})
    new_history = history_state + [{"role": "user", "content": text}]
    return new_history, gr.update(value="", interactive=False)


def add_file(history_state, file):
    """
    处理文件上传
    """
    # 使用 Gradio 支持的文件消息格式
    new_history = history_state + [{
        "role": "user", 
        "content": [("file", file.name)]  # 文件消息格式
    }]
    return new_history


def bot(history_state):
    """
    处理AI回复（全部使用流式传输）
    """
    global messages
    
    # 使用流式传输生成器
    response_generator = chat(messages)
    response = ""
    
    # 添加初始的 assistant 消息占位符
    new_history = history_state + [{"role": "assistant", "content": ""}]
    
    # 逐步获取流式响应
    for chunk in response_generator:
        response += chunk
        # 实时更新最后一条助手消息
        new_history[-1] = {"role": "assistant", "content": response}
        yield new_history
    
    # 将最终回复添加到 messages
    messages.append({"role": "assistant", "content": response})


def clear_chat():
    """
    清空聊天记录
    """
    global messages, history
    messages = []
    history = []
    return []


with gr.Blocks() as demo:
    # 修复这里：移除了多余的括号
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        avatar_images=(None, os.path.join(os.path.dirname(__file__), "avatar.png")),
        type="messages"  # 指定使用新消息格式
    )

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="输入文字或指令（如/search 内容）",
            container=False,
        )
        clear_btn = gr.Button('清空')
        btn = gr.UploadButton("📁", file_types=["image", "video", "audio", "text"])

    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
        bot, chatbot, chatbot
    )
    txt_msg.then(lambda: gr.update(interactive=True), None, [txt], queue=False)
    
    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False)
    
    clear_btn.click(clear_chat, None, chatbot, queue=False)

demo.queue()
demo.launch()