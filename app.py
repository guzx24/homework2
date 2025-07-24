import gradio as gr
import os
import time
from chat import chat

# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.

messages = []

current_file_text = None

def add_text(history, text):
    """
    处理用户输入文本, 添加到messages中, 并返回历史记录和更新输入框
    """
    global messages 

    
    history = history + [(text, None)]
    messages.append({"role": "user", "content": text})
    return history, gr.update(value="", interactive=False)


def add_file(history, file):
    """
    处理用户上传文件, 添加到messages中, 并返回历史记录
    """
    global messages
    history = history + [((file.name,), None)]
    messages.append({"role": "user", "content": file.name})
    return history


def bot(history):
    """
    生成AI助手的回复
    """
    global messages

    try:
        # 获取AI回复
        response = chat(messages)
        
        # 更新聊天记录
        messages.append({"role": "assistant", "content": response})
        
        # 更新最后一条历史记录的回复部分
        if history and history[-1][1] is None:
            history[-1] = (history[-1][0], response)
        else:
            history = history + [(None, response)]
            
    except Exception as e:
        error_msg = f"⚠️ error: {str(e)}"
        history[-1] = (history[-1][0], error_msg)
    return history

def clear_chat(history):
    """
    清除聊天记录
    """
    global messages
    messages.clear()
    history.clear()
    return history

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        avatar_images=(None, (os.path.join(os.path.dirname(__file__), "avatar.png"))),
    )

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter text and press enter, or upload an image",
            container=False,
        )
        clear_btn = gr.Button('Clear')
        btn = gr.UploadButton("📁", file_types=["image", "video", "audio", "text"])

    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
        bot, chatbot, chatbot
    )
    txt_msg.then(lambda: gr.update(interactive=True), None, [txt], queue=False)
    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear_btn.click(lambda: messages.clear(), None, chatbot, queue=False)

demo.queue()
demo.launch()

