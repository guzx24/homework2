import torch
import torchvision.transforms as transforms
from PIL import Image
from lenet import LeNet  # Import the LeNet model definition from lenet.py

# Path to the pre-trained model weights
MODEL_PATH = "lenet.pth"

# Load the model
try:
    # Initialize the model structure. [cite_start]It must match the one used for training. [cite: 319]
    # The LeNet class is defined in the provided lenet.py file.
    model = LeNet(num_classes=10)

    # [cite_start]Load the trained weights into the model structure. [cite: 319]
    # [cite_start]The state dictionary keys in lenet.pth must match the layer names in the LeNet class. [cite: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
    # Load the outer dictionary, and then access the nested 'state_dict'.
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu'))['state_dict'])

    # Set the model to evaluation mode. This is important for inference.
    model.eval()
except FileNotFoundError:
    print(f"Error: Model file not found at {MODEL_PATH}")
    model = None
except Exception as e:
    print(f"An error occurred while loading the model: {e}")
    model = None

# Define the image transformation pipeline.
# The model was trained on 28x28 grayscale images.
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),  # Convert image to grayscale
    transforms.Resize((28, 28)),  # Resize to 28x28 pixels
    transforms.ToTensor(),  # Convert to a PyTorch tensor
    transforms.Normalize((0.5,), (0.5,))  # Normalize tensor values
])


def image_classification(file):
    """
    Receives an image file, preprocesses it, and returns the classification result
    from the pre-trained LeNet model.

    Args:
        file (gradio.File): The uploaded image file object from Gradio.

    Returns:
        str: A string with the classification result, e.g., "Classification result: 5".
    """
    if model is None:
        return "Classification failed: Model is not loaded."

    try:
        # Open the image using PIL
        img = Image.open(file.name).convert("RGB")

        # Apply the defined transformations
        img_tensor = transform(img)

        # Add a batch dimension (the model expects a batch of images)
        img_batch = img_tensor.unsqueeze(0)

        # Perform prediction
        with torch.no_grad():
            output = model(img_batch)

        # Get the predicted class index
        _, predicted = torch.max(output.data, 1)
        result = predicted.item()

        # [cite_start]Return the formatted result string as required. [cite: 319]
        return f"Classification result: {result}"

    except Exception as e:
        return f"An error occurred during classification: {e}"