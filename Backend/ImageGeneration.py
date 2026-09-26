import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import dotenv_values
import os
from time import sleep

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "Data")
FILES_DIR = os.path.join(PROJECT_ROOT, "Frontend", "Files")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)

env_vars = dotenv_values(os.path.join(PROJECT_ROOT, ".env"))
HuggingFaceAPIKey = env_vars.get("HuggingFaceAPIKey", "")

# Function to open and display generated images
def open_image(prompt):
    folder_path = DATA_DIR
    prompt = prompt.replace(" ", "_")

    # List of generated images
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            # Open and display the image
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)

        except IOError:
            print(f"Unable to open image: {image_path}") 

# API details
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large"
headers = {"Authorization": f"Bearer {HuggingFaceAPIKey}"}

# Function to query the API
async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

# Function to generate multiple images based on prompt
async def generate_images(prompt: str):
    tasks = []  # List to store async tasks

    # Create 4 different tasks for image generation
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}",     
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    # Wait for all tasks to finish and gather the results
    image_bytes_list = await asyncio.gather(*tasks)

    # Save the images to disk
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes is not None:  # Check if the image bytes are valid
            img_file = os.path.join(DATA_DIR, f"{prompt.replace(' ','_')}{i + 1}.jpg")
            with open(img_file, "wb") as f:
                f.write(image_bytes)
        else:
            print(f"Image generation failed for task {i + 1}")

# Function to be called in the main logic
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))  # Run the async image generation
    open_image(prompt)  # Open and display the generated images

if __name__ == "__main__":
    image_gen_data_path = os.path.join(FILES_DIR, "ImageGeneration.data")
    while True:
        try:
            # Read the status from the file to see if image generation is requested
            with open(image_gen_data_path, "r", encoding="utf-8") as f:
                Data = f.read()

            prompt, Status = Data.split(",")

            # If the status is "True", start the image generation process
            if Status.strip() == "True":  # Strip whitespace
                print("Generating Images...")
                GenerateImages(prompt=prompt)

                # Set status to "False" after the image generation is done
                with open(image_gen_data_path, "w", encoding="utf-8") as f:
                    f.write("False,False")  # Reset status after generating images
                break  # Exit loop after generating images

            else:
                sleep(1)  # Wait for 1 second before checking the status again

        except Exception:
            sleep(1)