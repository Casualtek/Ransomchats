import json
import os
from github import Github  # PyGithub library
from datetime import datetime
import requests
import base64

def count_messages_in_chat(content_data):
    """Count messages in a chat JSON structure"""
    try:
        if isinstance(content_data, dict):
            # Look for messages array or similar structure
            if 'messages' in content_data:
                return len(content_data['messages'])
            elif 'chat' in content_data and isinstance(content_data['chat'], list):
                return len(content_data['chat'])
            elif isinstance(content_data, list):
                return len(content_data)
        elif isinstance(content_data, list):
            return len(content_data)
        return 0
    except Exception as e:
        print(f"Error counting messages: {str(e)}")
        return 0

def generate_chat_index():
    # Initialize GitHub client
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    
    g = Github(github_token)
    repo = g.get_repo("Casualtek/Ransomchats")
    
    # Get all directories in the root (groups)
    contents = repo.get_contents("")
    groups = [c for c in contents if c.type == "dir" and c.name != "parsers" and c.name != ".github"]
    
    chat_index = {
        "last_updated": datetime.utcnow().isoformat(),
        "statistics": {
            "total_groups": 0,
            "total_chats": 0,
            "total_messages": 0
        },
        "groups": {}
    }
    
    total_chats = 0
    total_messages = 0
    
    # Process each group
    for group in groups:
        group_name = group.name
        chat_index["groups"][group_name] = {
            "chats": [],
            "group_statistics": {
                "chat_count": 0,
                "message_count": 0
            }
        }
        
        group_chat_count = 0
        group_message_count = 0
        
        try:
            # Get all JSON files in the group directory
            files = repo.get_contents(group_name)
            for file in files:
                if file.name.endswith('.json'):
                    # Get file content to count messages
                    try:
                        # Decode base64 content
                        content_data = json.loads(base64.b64decode(file.content).decode('utf-8'))
                        message_count = count_messages_in_chat(content_data)
                    except Exception as e:
                        print(f"Error reading {file.name}: {str(e)}")
                        message_count = 0
                    
                    chat_info = {
                        "filename": file.name,
                        "chat_id": file.name.replace('.json', ''),
                        "raw_url": f"https://raw.githubusercontent.com/Casualtek/Ransomchats/main/{group_name}/{file.name}",
                        "message_count": message_count
                    }
                    
                    chat_index["groups"][group_name]["chats"].append(chat_info)
                    group_chat_count += 1
                    group_message_count += message_count
                    
        except Exception as e:
            print(f"Error processing group {group_name}: {str(e)}")
            continue
        
        # Update group statistics
        chat_index["groups"][group_name]["group_statistics"]["chat_count"] = group_chat_count
        chat_index["groups"][group_name]["group_statistics"]["message_count"] = group_message_count
        
        total_chats += group_chat_count
        total_messages += group_message_count
    
    # Update overall statistics
    chat_index["statistics"]["total_groups"] = len(groups)
    chat_index["statistics"]["total_chats"] = total_chats
    chat_index["statistics"]["total_messages"] = total_messages
    
    # Save index file
    with open("chat_index.json", "w") as f:
        json.dump(chat_index, f, indent=2)
    
    return chat_index

if __name__ == "__main__":
    try:
        index = generate_chat_index()
        print(f"Generated index with:")
        print(f"  - {index['statistics']['total_groups']} groups")
        print(f"  - {index['statistics']['total_chats']} chats")
        print(f"  - {index['statistics']['total_messages']} messages")
        
        # Print group breakdown
        for group_name, group_data in index['groups'].items():
            stats = group_data['group_statistics']
            print(f"  - {group_name}: {stats['chat_count']} chats, {stats['message_count']} messages")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Make sure to set your GITHUB_TOKEN environment variable:")
        print("export GITHUB_TOKEN='your_github_token_here'")
