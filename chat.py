import os
import json
import zipfile
import google.generativeai as genai
from dotenv import load_dotenv
import time
import sys
load_dotenv()

genai.configure(api_key=os.getenv("API_KEY"))

def get_user_input():
    print("Welcome to the application generator")
    user_input = input("Enter the details of the application to generate:\n")
    return user_input

def send_prompt_to_ai(user_input):
    generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 0,
        "max_output_tokens": 2048,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.0-pro",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(
        history=[]
    )

    prompt = f"""
    Generate an application based on the following details: {user_input}
    The response of AI should be strictly in JSON format(nothing other than json format) with 'path' and 'content' as key-value pairs for each file. The structure should be followed for any type of file extension not necessarily what shown in example.The structure should use double quotes for strings and look like this max file limit is 20 files:
    [
        {{"path": "file.extension", "content": "the file content"}},
        {{"path": "file.extension", "content": "body {{ ... }}"}}
    ]
    """

    response = chat_session.send_message(prompt)
    return response.text

def preprocess_response(response):
    print("Raw AI Response:")
    print(response)
    #response = response.strip()
    try:
        file_structure = json.loads(response)
        if isinstance(file_structure, list) and all('path' in f and 'content' in f for f in file_structure):
            return file_structure
        else:
            raise ValueError("Response is not in expected format")
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        raise ValueError("AI response is not a valid JSON")

def generate_files(file_structure):
    if not os.path.exists("application_files"):
        os.mkdir("application_files")
    for file_info in file_structure:
        file_path = os.path.join("application_files", file_info['path'].lstrip("/"))
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            file.write(file_info['content'])

def zip_generated_files():
    with zipfile.ZipFile("application_files.zip", "w") as zipf:
        for root, dirs, files in os.walk("application_files"):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file), "application_files"))

def main():
    filepath=sys.argv[1]
    with open(filepath, 'r') as file:
        user_input = file.read()
        print("File Content:\n")
        print(user_input)
    
    #user_input = get_user_input()
    response = send_prompt_to_ai(user_input)
    print("Response from the AI:")
    print(response)
    
    try:
        file_structure = preprocess_response(response)
        generate_files(file_structure)
        zip_generated_files()
        print("Application generated and saved as 'application_files.zip' in the current directory.")
    except ValueError as e:
        print(f"Error processing AI response: {e}")
    time.sleep(60)


if __name__ == "__main__":
    main()
   
