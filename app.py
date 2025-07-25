import gradio as gr
import os
from chat import chat
from fetch import fetch
from image_generate import image_generate  # 1. Import the image generation function

# --- Gradio UI 布局与事件处理 ---
with gr.Blocks() as demo:
    # State managers
    model_messages = gr.State([])
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
            placeholder="Enter text or a command (e.g., /image a cat)",
            container=False,
        )
        clear_btn = gr.Button('清空')
        upload_btn = gr.UploadButton("📁", file_types=["image", "video", "audio", "text"])


    # 2. A new unified handler to replace the previous event chain
    def unified_handler(user_input, ui_history, model_history):
        """
        Handles all user input, dispatching to the correct function (image generation or chat).
        This function is a generator, yielding UI updates at each step.
        """
        # Step 1: Add user's message to UI and disable the input box
        ui_history.append({"role": "user", "content": user_input})
        yield ui_history, model_history, gr.update(value="", interactive=False)

        # --- Command Dispatcher ---
        # [cite_start]3. Handle '/image' command [cite: 251]
        if user_input.startswith('/image '):
            prompt = user_input[7:].strip()
            # Add a placeholder while the image is being generated
            ui_history.append({"role": "assistant", "content": "Generating image, please wait..."})
            yield ui_history, model_history, gr.update(interactive=False)

            try:
                # Call the function from image_generate.py
                image_url = image_generate(prompt)

                # [cite_start]Update the backend model history for context/logging [cite: 243]
                model_history.append({"role": "user", "content": user_input})
                model_history.append({"role": "assistant", "content": image_url})

                # Update the UI to display the generated image. [cite_start]Gradio renders image URLs automatically. [cite: 244]
                ui_history[-1]["content"] = image_url
            except Exception as e:
                error_message = f"Image generation failed: {e}"
                print(f"--- [app.py] {error_message} ---")
                ui_history[-1]["content"] = error_message

            # Re-enable the input box and finish
            yield ui_history, model_history, gr.update(interactive=True)
            return

        # --- Default and other commands that use the Language Model ---

        # Prepare the prompt for the language model
        if user_input.startswith('/fetch '):
            url = user_input[6:].strip()
            question = fetch(url)
            model_history.append({"role": "user", "content": question})
        else:
            # For normal chat, the user input is the prompt
            model_history.append({"role": "user", "content": user_input})

        # --- Stream Language Model Response ---
        ui_history.append({"role": "assistant", "content": ""})

        response_generator = chat(model_history)
        full_response = ""

        for chunk in response_generator:
            full_response += chunk
            ui_history[-1]["content"] = full_response
            yield ui_history, model_history, gr.update(interactive=False)

        model_history.append({"role": "assistant", "content": full_response})
        yield ui_history, model_history, gr.update(interactive=True)


    def clear_chat_history():
        """Clears both the UI and the backend model history."""
        return [], []


    # --- Event Binding ---
    # 4. Bind the new unified handler to the submit event
    txt_input.submit(
        unified_handler,
        [txt_input, chatbot_ui, model_messages],
        [chatbot_ui, model_messages, txt_input]
    )

    clear_btn.click(
        clear_chat_history,
        None,
        [chatbot_ui, model_messages],
        queue=False
    )


    def add_file_to_ui(ui_history, file):
        ui_history.append({"role": "user", "content": f"File uploaded: {os.path.basename(file.name)}"})
        ui_history.append({"role": "assistant", "content": "File received. Please tell me what to do with it."})
        return ui_history


    upload_btn.upload(add_file_to_ui, [chatbot_ui, upload_btn], [chatbot_ui], queue=False)

demo.queue()
demo.launch()