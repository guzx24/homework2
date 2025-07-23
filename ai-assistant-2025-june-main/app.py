# import gradio as gr
# import os
# from chat import chat
# from search import search

# # --- Gradio UI 布局与事件处理 ---
# with gr.Blocks() as demo:
#     # 状态管理器
#     model_messages = gr.State([])  # 模型对话历史（OpenAI格式）
#     chat_history = gr.State([])    # UI聊天历史（Gradio格式）
    
#     # Chatbot UI 组件
#     chatbot = gr.Chatbot(
#         [],
#         elem_id="chatbot",
#         avatar_images=(None, os.path.join(os.path.dirname(__file__), "avatar.png")),
#         height=600,
#         label="AI Assistant"
#     )

#     with gr.Row():
#         txt_input = gr.Textbox(
#             scale=4,
#             show_label=False,
#             placeholder="输入文字或指令（如/search 内容）",
#             container=False,
#         )
#         clear_btn = gr.Button('清空')
#         upload_btn = gr.UploadButton("📁", file_types=["text"])

#     # --- 事件处理函数 ---
#     def handle_user_submission(user_input, chat_hist, model_hist):
#         """处理用户输入（含特殊指令）"""
#         print(f"用户输入: {user_input}")
        
#         # 处理/search指令
#         if user_input.startswith('/search'):
#             query = user_input[8:].strip()
#             print(f"处理搜索指令: {query}")
#             try:
#                 processed_content = search(query)  # 调用搜索函数
#                 print(f"搜索结果: {processed_content[:50]}...")
                
#                 # 更新模型历史（使用处理后的内容）
#                 model_hist.append({"role": "user", "content": processed_content})
                
#                 # 更新UI历史（显示原始指令）
#                 new_chat_hist = chat_hist + [(f"/search {query}", None)]
#                 return new_chat_hist, model_hist, gr.update(value="", interactive=False)
#             except Exception as e:
#                 print(f"搜索出错: {e}")
#                 error_msg = f"⚠️ 搜索失败: {str(e)}"
#                 new_chat_hist = chat_hist + [(f"/search {query}", error_msg)]
#                 model_hist.append({"role": "assistant", "content": error_msg})
#                 return new_chat_hist, model_hist, gr.update(value="", interactive=True)
        
#         # 普通消息
#         model_hist.append({"role": "user", "content": user_input})
#         new_chat_hist = chat_hist + [(user_input, None)]
#         print(f"更新聊天历史: {new_chat_hist}")
#         return new_chat_hist, model_hist, gr.update(value="", interactive=False)

#     def stream_bot_response(chat_hist, model_hist):
#         """流式生成AI回复"""
#         print(f"开始生成AI响应, 模型历史长度: {len(model_hist)}")
        
#         # 创建临时响应占位符
#         chat_hist = chat_hist.copy()  # 避免修改原始状态
#         if chat_hist and chat_hist[-1][1] is None:
#             chat_hist[-1] = (chat_hist[-1][0], "")
        
#         try:
#             full_response = ""
#             cursor = "▌"  # 光标指示器
            
#             # 获取流式响应
#             for chunk in chat(model_hist):
#                 if chunk:
#                     full_response += chunk
#                     # 实时更新最后一条AI消息
#                     chat_hist[-1] = (chat_hist[-1][0], full_response + cursor)
#                     yield chat_hist
            
#             # 流式结束：移除光标并更新状态
#             chat_hist[-1] = (chat_hist[-1][0], full_response)
#             model_hist.append({"role": "assistant", "content": full_response})
#             print(f"AI响应完成: {full_response[:50]}...")
#             yield chat_hist
            
#         except Exception as e:
#             print(f"生成错误: {e}")
#             error_msg = f"⚠️ 服务暂时不可用，请稍后再试（错误代码：{str(e)}）"
#             chat_hist[-1] = (chat_hist[-1][0], error_msg)
#             model_hist.append({"role": "assistant", "content": error_msg})
#             yield chat_hist

#     def re_enable_textbox():
#         """重新激活输入框"""
#         print("重新激活输入框")
#         return gr.update(interactive=True)

#     def clear_chat_history():
#         """清空聊天记录"""
#         print("清空聊天记录")
#         return [], []

#     # --- 事件绑定 ---
#     txt_input.submit(
#         handle_user_submission,
#         [txt_input, chat_history, model_messages],
#         [chat_history, model_messages, txt_input],
#         queue=False
#     ).then(
#         stream_bot_response,
#         [chat_history, model_messages],
#         [chat_history]
#     ).then(
#         re_enable_textbox,
#         None,
#         [txt_input]
#     )

#     clear_btn.click(
#         clear_chat_history,
#         None,
#         [chat_history, model_messages],
#         queue=False
#     )

#     # 文件上传功能
#     def add_file_to_ui(chat_hist, file):
#         """处理文件上传"""
#         print(f"上传文件: {file.name}")
#         new_chat_hist = chat_hist + [(f"📁 已上传文件: {os.path.basename(file.name)}", None)]
#         return new_chat_hist
    
#     upload_btn.upload(
#         add_file_to_ui, 
#         [chat_history, upload_btn], 
#         [chat_history], 
#         queue=False
#     ).then(
#         stream_bot_response,
#         [chat_history, model_messages],
#         [chat_history]
#     )

# demo.queue().launch(debug=True)



import gradio as gr
import os
from chat import chat
# 假设 search.py 存在且功能正确
# from search import search # 如果 search.py 未实现，可以先注释掉

# --- Gradio UI 布局与事件处理 ---
with gr.Blocks() as demo:
    # 状态管理器：使用 gr.State 独立维护模型的对话历史。
    # 这是与UI分离的、看不见的后端状态。
    model_messages = gr.State([])

    # Chatbot UI 组件：使用 Gradio 推荐的 'messages' 格式。
    chatbot_ui = gr.Chatbot(
        [],
        elem_id="chatbot",
        avatar_images=(None, os.path.join(os.path.dirname(__file__), "avatar.png")),
        height=600,
        label="AI Assistant",
        type='messages'  # 关键：切换到新的消息格式
    )

    with gr.Row():
        txt_input = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="输入文字或指令（如/search 内容）",
            container=False,
        )
        clear_btn = gr.Button('清空')
        upload_btn = gr.UploadButton("📁", file_types=["image", "video", "audio", "text"])

    # --- 事件处理函数 ---
    def handle_user_submission(user_input, ui_history, model_history):
        """
        处理用户输入，更新UI和后端模型状态。
        """
        # 简单的指令处理
        # if user_input.startswith('/search'):
        #     query = user_input[8:].strip()
        #     processed_prompt = search(query)
        #     model_history.append({"role": "user", "content": processed_prompt})
        # else:
        model_history.append({"role": "user", "content": user_input})
        
        # 更新前端UI的状态
        ui_history.append({"role": "user", "content": user_input})
        
        # 返回更新后的状态，并禁用文本框
        return ui_history, model_history, gr.update(value="", interactive=False)

    def stream_bot_response(ui_history, model_history):
        """
        流式处理并显示AI的回复。
        """
        # 为AI的回复在UI上准备一个占位符
        ui_history.append({"role": "assistant", "content": ""})
        
        # 从 chat.py 获取流式回复
        response_generator = chat(model_history)
        full_response = ""
        
        # 迭代生成器的每个块，并更新UI
        for chunk in response_generator:
            full_response += chunk
            ui_history[-1]["content"] = full_response
            yield ui_history
            
        # 流式传输完成后，将完整的回复添加到后端模型状态中以供记忆
        model_history.append({"role": "assistant", "content": full_response})

    def re_enable_textbox():
        """重新激活文本输入框。"""
        return gr.update(interactive=True)

    def clear_chat_history():
        """清空后端状态和前端UI。"""
        return [], []

    # --- 事件绑定 ---
    txt_input.submit(
        handle_user_submission,
        [txt_input, chatbot_ui, model_messages],
        [chatbot_ui, model_messages, txt_input],
        queue=False
    ).then(
        stream_bot_response,
        [chatbot_ui, model_messages],
        [chatbot_ui]
    ).then(
        re_enable_textbox,
        None,
        [txt_input]
    )

    clear_btn.click(
        clear_chat_history,
        None,
        [chatbot_ui, model_messages],
        queue=False
    )
    
    # 文件上传功能（简化版，待后续实现具体逻辑）
    def add_file_to_ui(ui_history, file):
        ui_history.append({"role": "user", "content": f"已上传文件: {os.path.basename(file.name)}"})
        ui_history.append({"role": "assistant", "content": "文件已收到，请告诉我需要对它做什么。"})
        return ui_history
    
    upload_btn.upload(add_file_to_ui, [chatbot_ui, upload_btn], [chatbot_ui], queue=False)


demo.queue()
demo.launch()
