import json
import requests
import os
import subprocess
from datetime import datetime
import sys

def save_to_file(question, answer):
    with open("Capt_logs.txt", "a") as file:
        file.write(f"{datetime.now().strftime('%Y-%m-%d %I:%M %p')}: Question: {question}\n")
        file.write(f"{datetime.now().strftime('%Y-%m-%d %I:%M %p')}: Answer: {answer}\n\n")

def extract_bash_code(response):
    bash_code = []
    for choice in response['choices']:
        message = choice['message']['content']
        code_blocks = extract_code_from_message(message)
        bash_code.extend(code_blocks)
    return bash_code

def extract_code_from_message(message):
    code_blocks = []
    start_index = message.find("```bash")
    while start_index != -1:
        end_index = message.find("```", start_index + 7)
        if end_index != -1:
            code_blocks.append(message[start_index:end_index + 3])
        start_index = message.find("```bash", end_index + 3)
    return code_blocks

def save_bash_code_to_file(bash_code):
    file_name = f"bash_script_{datetime.now().strftime('%Y%m%d%H%M%S')}.sh"
    with open(file_name, "w") as file:
        file.write("#!/bin/bash\n")  # Add shebang line
        for code_block in bash_code:
            # Remove leading and trailing whitespace
            code_block = code_block.strip()
            # Remove leading ```bash and trailing ```
            code_block = code_block.replace("```bash", "").replace("```", "")
            file.write(code_block + "\n\n")
        print(f"\nBash code extracted and saved to {file_name}\n")
        # Change file permissions
        os.chmod(file_name, 0o755)
        return file_name

def execute_bash_script(file_name):
    try:
        subprocess.run(["./" + file_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Failed to execute {file_name}")

url = "https://chat.tune.app/api/chat/completions"
headers = {
    "Authorization": "tune-faa88cbb-18f8-4a97-a909-b1fae72430c81710549351",
    "Content-Type": "application/json"
}
model = "goliath-120b-16k-gptq"

# Display instructions
print("--------------------------------------------------")
print(" Hello, my name is Professor Bash.                ")
print(" I can answer any bash scripting questions.       ")
print(" Type 'e' to exit the conversation.              ")
print("--------------------------------------------------")

while True:
    user_input = input("--------------------------------------------------\n Ask Professor Bash >> ")
    if user_input.lower() == 'e':
        print("--------------------------------------------------")
        print(" Exiting conversation.")
        print("--------------------------------------------------")
        break  # Exit the loop
    if user_input.strip() != '':
        data = {
            "temperature": 0.5,
            "messages": [
                {
                    "role": "system",
                    "content": "Your name is Professor Bash, if asked what your name is you always answer Professor Bash.You are an expert in coding with bash script and the best in the world at coding in bash script, you know everything about bash script and create the best bash scripts in the world. You always answer any question i ask about Bash Script and write all of the bash script code i ask you to write. You know everything their is to know about bash script. You know every bash script command and how to use every bash script command. You are an excellent teacher and love teaching people how to use bash script. You love writing bash script code and can write any type of bash script anyone needs.You live to write bash script and answer every question i ask you about bash script."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            "model": model,
            "stream": False,
            "max_tokens": 1000
        }

        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        answer = response_json['choices'][0]['message']['content']
        print("--------------------------------------------------")
        print(" Professor Bash Says >>", answer)
        print("--------------------------------------------------")

        bash_code = extract_bash_code(response_json)
        if bash_code:
            file_name = save_bash_code_to_file(bash_code)
            execute_bash_script(file_name)
        else:
            print(" No bash code found in the response, I did not automatically run any code for you this time.")
            print("--------------------------------------------------")

        save_to_file(user_input, answer)
