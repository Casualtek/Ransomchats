#!/usr/bin/python3
import os
import sys
import json
from bs4 import BeautifulSoup

def parse_html_to_json(html_file, output_file):
    # Load the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    print(f'Parsing {html_file}.')

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the chat ID
    chat_idDiv = soup.find('div', class_='logout')
    if chat_idDiv is not None:
        chat_id = chat_idDiv.get_text().strip()
    else:
        chat_id = ''

    # Find all chat items
    chat      = soup.find('div', class_='chat-body')
    chat_days = chat.find_all('div', attrs={'data-v-43568220=': ''})

    # Extract party and message details for each chat item
    messages = []
    for day in chat_days:
        date = day.find('div', class_='chat-date')
        if date is not None:
            chat_items = day.find_all('div', class_='chat-item')
        
            for item in chat_items:
                if item is not None:
                    # Determine the party based on the class
                    if 'incoming' in item['class']:
                        party = 'Victim'
                    elif 'incoming' not in item['class']:
                        party = 'Hive'
                    else:
                        continue  # Skip if the class is neither 'chat-item-income' nor 'chat-item-out'
                    # Extract message content and timestamp
                    message_text = item.find('div', class_='chat-message')
                    if message_text is not None:
                        content = message_text.get_text().strip()
                    message_time = item.find('div', class_='chat-message-time')
                    if message_time is not None:
                        time = message_time.get_text().strip()
                        message = {
                            'party': party,
                            'content': content,
                            'timestamp': date.get_text().strip()+' '+time
                        }
                        messages.append(message)
                else:
                    continue

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
