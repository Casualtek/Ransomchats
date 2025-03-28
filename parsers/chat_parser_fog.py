#!/usr/bin/python3
import os
import sys
import json
from bs4 import BeautifulSoup

# Constants for repeated strings
HTML_PARSER = 'html.parser'
CHAT_MESSAGES_CLASS = 'chat-messages'
G_BOX_FLEX_CLASS = 'g-box g-flex'
DATE_SPAN_CLASS = 'g-text g-text_variant_body-1 g-color-text g-color-text_color_secondary'
MESSAGE_LEFT_CLASS = 'g-box g-flex g-flex_s_2 left'
MESSAGE_RIGHT_CLASS = 'g-box g-flex g-flex_s_2 right'
MESSAGE_CLASS = 'g-box g-flex g-flex_s_2'
MESSAGE_DETAILS_CLASS = 'g-flex__wr'

def parse_html_to_json(html_file, output_folder):
    """
    Parses an HTML file to extract chat messages and saves them as a JSON file.

    :param html_file: Path to the input HTML file.
    :param output_folder: Path to the output folder where the JSON file will be saved.
    """
    try:
        # Load the HTML file
        with open(html_file, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html_content, HTML_PARSER)

        # Extract the chat ID (currently not used)
        chat_id = ''

        # Find all chat items
        chat_container = soup.find('div', class_=CHAT_MESSAGES_CLASS)
        chat_subcontainer = chat_container.find('div', class_=G_BOX_FLEX_CLASS)
        full_chat = chat_subcontainer.find('div', class_=G_BOX_FLEX_CLASS)

        messages = []
        current_date = None

        for div in full_chat.find_all('div', class_=G_BOX_FLEX_CLASS):
            date_span = div.find('span', class_=DATE_SPAN_CLASS)
            if date_span and "text-align: center" in date_span.get('style', ''):
                current_date = date_span.text.strip()

            message_div = div.find('div', class_=MESSAGE_LEFT_CLASS)
            if message_div:
                party = 'fog'
            else:
                message_div = div.find('div', class_=MESSAGE_RIGHT_CLASS)
                party = 'victim' if message_div else div.find('div', class_=MESSAGE_CLASS)

            if message_div:
                message_details = message_div.find_all('div', class_=MESSAGE_DETAILS_CLASS)
                if len(message_details) >= 2:
                    message_contents = message_details[0].text.strip()
                    message_time = message_details[1].text.strip()
                    if current_date:
                        timestamp = f'{current_date} {message_time}'
                        messages.append({'timestamp': timestamp, 'party': party, 'message': message_contents})

        # Get the output file name from the input HTML file name
        output_filename = os.path.splitext(os.path.basename(html_file))[0] + '.json'
        output_path = os.path.join(output_folder, output_filename)

        # Write the chat data to a JSON file
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(messages, json_file, indent=4)

        print(f'Chat data extracted and saved as {output_path}')

    except Exception as e:
        print(f'Error processing {html_file}: {e}')

def main():
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 3:
        print('Usage: python script.py input_folder output_folder')
        return

    # Get the input folder and output folder paths from command-line arguments
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    # Iterate through HTML files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.html'):
            input_file = os.path.join(input_folder, filename)
            print(f'Processing {filename}')
            parse_html_to_json(input_file, output_folder)

if __name__ == '__main__':
    main()
