import gradio as gr
import os
from chat import chat
from fetch import fetch
from image_generate import image_generate
# [cite_start]Import the functions for file processing from pdf.py. [cite: 269, 270, 271]
from pdf import generate_summary, generate_question, generate_text
from mnist import image_classification # <-- ADD THIS LINE
# [cite_end]
# [cite_end]

# --- Gradio UI 布局与事件处理 ---
with gr.Blocks() as demo:
    # State managers
    model_messages = gr.State([])
    # [cite_start]Add a state to store the content of the currently loaded .txt file. [cite: 254]
    current_file_text = gr.State("")
    # [cite_end]

    chatbot_ui = gr.Chatbot(
        [],
        elem_id="chatbot",
        avatar_images=(None, os.path.join(os.path.dirname(__file__), "avatar.png")),
        height=600,
        label="AI Assistant",
        type='messages'
    )

    with gr.Row():
        txt_input = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Upload a .txt file or enter a command (e.g., /file Who is...)",
            container=False,
        )
        clear_btn = gr.Button('清空')
        # [cite_start]Allow uploading of text files. [cite: 254]
        upload_btn = gr.UploadButton("📁", file_types=["text", "image"])
        # [cite_end]


    def unified_handler(user_input, ui_history, model_history, file_text):
        ui_history.append({"role": "user", "content": user_input})
        yield ui_history, model_history, file_text, gr.update(value="", interactive=False)

        # --- Command Dispatcher ---
        if user_input.startswith('/image '):
            prompt = user_input[7:].strip()
            ui_history.append({"role": "assistant", "content": "Generating image..."})
            yield ui_history, model_history, file_text, gr.update(interactive=False)
            try:
                image_url = image_generate(prompt)
                model_history.append({"role": "user", "content": user_input})
                model_history.append({"role": "assistant", "content": image_url})
                ui_history[-1]["content"] = image_url
            except Exception as e:
                ui_history[-1]["content"] = f"Image generation failed: {e}"
            yield ui_history, model_history, file_text, gr.update(interactive=True)
            return

        # [cite_start]Add handler for the '/file' command. [cite: 273]
        elif user_input.startswith('/file '):
            if not file_text:
                ui_history.append(
                    {"role": "assistant", "content": "Please upload a .txt file before using the /file command."})
                yield ui_history, model_history, file_text, gr.update(interactive=True)
                return

            content = user_input[6:].strip()
            # [cite_start]Generate a question prompt from the file content and user query. [cite: 271, 273]
            question_prompt = generate_question(file_text, content)
            # [cite_end]
            # [cite_start]Update the backend model history with the user's command. [cite: 254]
            model_history.append({"role": "user", "content": user_input})
            # [cite_end]
            ui_history.append({"role": "assistant", "content": ""})

            # [cite_start]Call the streaming text generation function for the answer. [cite: 269, 273, 274]
            response_generator = generate_text(question_prompt)
            # [cite_end]
            full_response = ""
            for chunk in response_generator:
                full_response += chunk
                ui_history[-1]["content"] = full_response
                yield ui_history, model_history, file_text, gr.update(interactive=False)

            # [cite_start]Update model history with the final generated answer. [cite: 259]
            model_history.append({"role": "assistant", "content": full_response})
            # [cite_end]
            yield ui_history, model_history, file_text, gr.update(interactive=True)
            return
        # [cite_end]

        # --- Default Chat ---
        else:
            model_history.append({"role": "user", "content": user_input})
            ui_history.append({"role": "assistant", "content": ""})
            response_generator = chat(model_history)
            full_response = ""
            for chunk in response_generator:
                full_response += chunk
                ui_history[-1]["content"] = full_response
                yield ui_history, model_history, file_text, gr.update(interactive=False)
            model_history.append({"role": "assistant", "content": full_response})
            yield ui_history, model_history, file_text, gr.update(interactive=True)


    def clear_chat_history():
        return [], [], ""


    # [cite_start]Implement the file upload handler function. [cite: 272]
    def handle_file_upload(file, ui_history, model_history, current_file_text):
        if file is not None and file.name.lower().endswith(".txt"):
            filename = os.path.basename(file.name)
            ui_history.append({"role": "user", "content": f"File uploaded: {filename}"})
            yield ui_history, model_history, "", gr.update(interactive=False)

            try:
                with open(file.name, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                summary_prompt = generate_summary(file_content)
                model_history.append({"role": "user", "content": summary_prompt})
                ui_history.append({"role": "assistant", "content": ""})

                response_generator = generate_text(summary_prompt)
                full_response = ""
                for chunk in response_generator:
                    full_response += chunk
                    ui_history[-1]["content"] = full_response
                    yield ui_history, model_history, file_content, gr.update(interactive=False)

                model_history.append({"role": "assistant", "content": full_response})
                yield ui_history, model_history, file_content, gr.update(interactive=True)
            except Exception as e:
                ui_history.append({"role": "assistant", "content": f"Error processing file: {e}"})
                yield ui_history, model_history, "", gr.update(interactive=True)

        # [cite_start]Add a new branch to handle PNG image file uploads for classification. [cite: 326]
        elif file is not None and file.name.lower().endswith((".png", ".jpg", ".jpeg")):
            filename = os.path.basename(file.name)

            # [cite_start]Display the uploaded image in the UI history. [cite: 319]
            # Add a 'content' key, which can be None or an empty string.
            ui_history.append({"role": "user", "content": "", "files": [file.name]})
            yield ui_history, model_history, current_file_text, gr.update(interactive=False)

            # [cite_start]Update the backend model history as per requirements. [cite: 319]
            model_history.append({"role": "user", "content": f"Please classify {filename}"})

            try:
                # [cite_start]Call the classification function from mnist.py. [cite: 325, 326]
                result_text = image_classification(file)

                # [cite_start]Update backend model history with the assistant's response. [cite: 319]
                model_history.append({"role": "assistant", "content": result_text})

                # Display the classification result in the UI.
                ui_history.append({"role": "assistant", "content": result_text})

            except Exception as e:
                error_message = f"Error classifying image: {e}"
                ui_history.append({"role": "assistant", "content": error_message})

            yield ui_history, model_history, current_file_text, gr.update(interactive=True)
        # [cite_end]
        else:
            ui_history.append({"role": "user", "content": "File upload attempted."})
            ui_history.append({"role": "assistant", "content": "This function only supports .txt and image files."})
            yield ui_history, model_history, current_file_text, gr.update(interactive=True)

    # [cite_end]
    # [cite_end]

    # --- Event Binding ---
    txt_input.submit(
        unified_handler,
        [txt_input, chatbot_ui, model_messages, current_file_text],
        [chatbot_ui, model_messages, current_file_text, txt_input]
    )

    clear_btn.click(
        clear_chat_history,
        None,
        [chatbot_ui, model_messages, current_file_text],
        queue=False
    )

    # [cite_start]Bind the upload handler to the upload button. [cite: 272]
    upload_btn.upload(
        handle_file_upload,
        [upload_btn, chatbot_ui, model_messages, current_file_text],  # <-- ADD current_file_text HERE
        [chatbot_ui, model_messages, current_file_text, txt_input],
        queue=True
    )
    # [cite_end]

demo.queue()
demo.launch()