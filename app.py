import gradio as gr
import os
import time
import requests
from chat import chat
from search import search
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

messages = []
current_file_text = None

def check_localai_health():
    """检查LocalAI服务是否可用"""
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            logger.info("LocalAI服务已启动并运行")
            return True
        return False
    except Exception as e:
        logger.error(f"无法连接到LocalAI服务: {str(e)}")
        return False

def add_text(history, text):
    global messages 
    
    # 检查LocalAI服务状态
    if not check_localai_health():
        history = history + [(text, "⚠️ 错误: 无法连接到LocalAI服务，请确保服务已启动")]
        return history, gr.update(value="", interactive=True)
    
    # 记录原始消息
    original_content = text
    
    if text.startswith("/search"):
        search_query = text[8:].strip()
        try:
            new_content = search(search_query)
            messages.append({"role": "user", "content": new_content})
        except Exception as e:
            logger.error(f"搜索错误: {str(e)}")
            history = history + [(text, f"⚠️ 搜索错误: {str(e)}")]
            return history, gr.update(value="", interactive=True)
    else:
        messages.append({"role": "user", "content": text})
    
    history = history + [(text, None)]
    
    return history, gr.update(value="", interactive=False)

def add_file(history, file):
    global messages
    history = history + [((file.name,), None)]
    messages.append({"role": "user", "content": file.name})
    return history

def bot(history):
    global messages

    try:
        response = ""
        
        # 流式获取响应
        for chunk in chat(messages):
            if chunk:
                response += chunk
                
                if history and history[-1][1] is None:
                    history[-1] = (history[-1][0], chunk)
                else:
                    if history and history[-1][1]:
                        history[-1] = (history[-1][0], history[-1][1] + chunk)
                    else:
                        history = history + [(None, chunk)]
                
                yield history
        
        if response:
            messages.append({"role": "assistant", "content": response})
            
    except Exception as e:
        logger.error(f"聊天错误: {str(e)}")
        error_msg = f"⚠️ 错误: {str(e)}"
        if history and history[-1][1] is None:
            history[-1] = (history[-1][0], error_msg)
        else:
            history = history + [(None, error_msg)]
        yield history

def clear_chat():
    global messages
    messages = []
    return []

# 应用启动时检查LocalAI服务
if not check_localai_health():
    logger.warning("LocalAI服务未运行，部分功能可能受限")

with gr.Blocks() as demo:
    gr.Markdown("# AI助手 - 基于LocalAI")
    
    with gr.Row():
        gr.Markdown("### 请确保LocalAI服务已运行: `docker compose up -d`")
    
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        avatar_images=(None, (os.path.join(os.path.dirname(__file__), "avatar.png"))),
    )

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="输入文本并按回车，或上传文件",
            container=False,
        )
        clear_btn = gr.Button('清空聊天')
        btn = gr.UploadButton("📁 上传文件", file_types=["image", "video", "audio", "text"])

    with gr.Row():
        gr.Markdown("**指令示例**: `/search 孙悟空` | `/image 可爱的海獭宝宝`")

    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
        bot, chatbot, chatbot
    )
    txt_msg.then(lambda: gr.update(interactive=True), None, [txt], queue=False)
    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear_btn.click(clear_chat, None, chatbot, queue=False)

demo.queue()
demo.launch()