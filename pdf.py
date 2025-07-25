import os
from openai import OpenAI

# Initialize the OpenAI client to connect to the local AI server.
# The API key is a placeholder as the local server does not require authentication.
client = OpenAI(base_url="http://localhost:8080/v1", api_key="not-needed")

def generate_text(prompt: str):
    """
    Calls the text completion API with a given prompt and streams the response.

    This function is a generator, yielding the text chunks as they are received from the model.
    The streaming functionality is required by the assignment to provide a better user experience.

    Args:
        prompt: The prompt to be sent to the text completion model.

    Yields:
        The text content from each chunk of the API's stream response.
    """
    # [MODIFIED] Use the chat completions endpoint to align with the working chat.py implementation.
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Change model to one that is known to work.
        messages=[{"role": "user", "content": prompt}], # Wrap the prompt in the required message format.
        stream=True,
    )
    for chunk in stream:
        # [MODIFIED] Adjust parsing to match the chat completions stream format.
        if chunk.choices[0].delta and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def generate_summary(current_file_text: str) -> str:
    """
    [cite_start]Creates a prompt to instruct the AI to summarize the provided text. [cite: 270]

    Args:
        current_file_text: The full text content of the uploaded file.

    Returns:
        A formatted string that serves as a summary prompt for the language model.
    """
    # [cite_start]Construct a prompt asking the model to summarize the file's content. [cite: 254, 270]
    summary_prompt = f"Act as a summarizer. Please summarize the following content:\n\n---\n\n{current_file_text}"
    return summary_prompt
    # [cite_end]


def generate_question(current_file_text: str, content: str) -> str:
    """
    [cite_start]Creates a prompt to answer a specific question based on the provided text. [cite: 271]

    Args:
        current_file_text: The full text content of the uploaded file (the context).
        content: The user's question about the text.

    Returns:
        A formatted string that serves as a question-answering prompt for the language model.
    """
    # [cite_start]Combine the file's text and the user's question into a single, effective prompt. [cite: 254, 271]
    question_prompt = f"Based on the following text, please answer the user's question.\n\n---TEXT---\n{current_file_text}\n\n---QUESTION---\n{content}"
    return question_prompt
    # [cite_end]