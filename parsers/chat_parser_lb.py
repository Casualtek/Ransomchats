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
    chat_id = soup.find('h3').get_text().strip()

    # Find all chat items
    chat_items = soup.find_all('div', class_='chat-item')

    # Extract party and message details for each chat item
    messages = []
    for item in chat_items:
        # Determine the party based on the class
        if 'chat-item-income' in item['class']:
            party = 'Victim'
        elif 'chat-item-out' in item['class']:
            party = 'LockBit 3.0'
        else:
            continue  # Skip if the class is neither 'chat-item-income' nor 'chat-item-out'

        # Extract message content and timestamp
        text_div = item.find('div', class_='text')
        date_div = item.find('div', class_='date')
        
        # Parsing message in a list to gather messages with line breaks, removing timestamp at the end of list
        content = text_div.get_text().strip().split('\n')[:-2]
        
        message = {
            'party': party,
            'content': " ".join(content), # Concatenate list items
            'timestamp': date_div.get_text().strip()
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
        if filename.endswith('.html'):
            # Get the input file path
            input_file = os.path.join(input_folder, filename)

            # Parse HTML and generate JSON
            parse_html_to_json(input_file, output_folder)
