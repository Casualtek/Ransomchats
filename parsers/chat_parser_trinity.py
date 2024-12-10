#!/usr/bin/python3
import os
import sys
import json
from bs4 import BeautifulSoup

def parse_html_to_json(html_file, output_file):
    # Load the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the chat ID
    # chat_id = soup.find('h3').get_text().strip()
    chat_id = ''

    # Find all chat items
    full_chat = soup.find('div', class_='msg_history')
    chat      = full_chat.find_all('div', recursive=False)
    
    messages = []
    for item in chat:
        if item['class'][0] == 'outgoing_msg':
            party = 'victim'
        else:
            party = 'trinity'
        message = item.find_all('p')
        if message != []:
            message = {
                'party': party,
                'content': message[0].get_text().strip(),
                'timestamp': ''
            }
            messages.append(message)

    # Create the JSON object with chat ID and messages
    chat_data = {
        'chat_id': chat_id,
        'messages': messages
    }

    # Get the output file name from the input HTML file name
    output_filename = os.path.splitext(os.path.basename(html_file))[0] + '.json'
    output_path = os.path.join(output_file, output_filename)

    # Write the chat data to a JSON file
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(chat_data, json_file, indent=4)

    print(f"Chat data extracted and saved as {output_path}")

# Check if the correct number of arguments is provided
if len(sys.argv) != 3:
    print("Usage: python script.py input_folder output_folder")
else:
    # Get the input folder and output folder paths from command-line arguments
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    # Iterate through HTML files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.htm'):
            # Get the input file path
            print(filename)
            input_file = os.path.join(input_folder, filename)

            # Parse HTML and generate JSON
            parse_html_to_json(input_file, output_folder)
