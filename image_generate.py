import os
from openai import OpenAI

# Configure the OpenAI client to connect to the local LocalAI server.
# As per the project instructions, the API key can be any non-empty string as it's not used for a local setup.
client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-needed"
)


def image_generate(content: str):
    """
    Calls the LocalAI stablediffusion model to generate an image based on a prompt.

    Args:
        [cite_start]content: The text prompt describing the desired image. [cite: 250]

    Returns:
        [cite_start]The URL of the generated image. [cite: 250]

    Raises:
        Exception: If the API call fails.
    """
    try:
        print(f"--- [image_generate.py] Generating image for prompt: '{content}' ---")

        # Call the image generation API endpoint.
        # [cite_start]The model is 'stablediffusion' [cite: 59] [cite_start]and the size is 256x256 as per the requirements. [cite: 252]
        response = client.images.generate(
            model="stablediffusion",
            prompt=content,
            n=1,
            size="256x256"
        )

        # [cite_start]The response object contains the URL of the image hosted by LocalAI. [cite: 243]
        image_url = response.data[0].url

        print(f"--- [image_generate.py] Image generated successfully. URL: {image_url} ---")

        return image_url

    except Exception as e:
        print(f"--- [image_generate.py] API call failed: {e} ---")
        # Re-raise the exception to be handled by the Gradio app
        raise


if __name__ == "__main__":
    # [cite_start]Example usage for testing the function directly, as shown in the project description. [cite: 246]
    try:
        url = image_generate('A cute baby sea otter')
        print(f"Generated image URL: {url}")
    except Exception as e:
        print(f"An error occurred during the test run: {e}")