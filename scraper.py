import os
import requests
from bs4 import BeautifulSoup

def get_latest_player():
    url = "https://pesdb.net/efootball/?all=1&sort=time_added"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching pesdb: {e}")
        return None
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for a_tag in soup.find_all('a'):
        href = a_tag.get('href', '')
        if '?id=' in href:
            try:
                player_id = href.split('?id=')[1].split('&')[0]
                player_name = a_tag.text.strip()
                if player_name and player_id.isdigit():
                    return {'id': player_id, 'name': player_name}
            except IndexError:
                continue
    
    return None

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"Failed to send message: {response.text}")
        else:
            print("Telegram message sent successfully.")
    except requests.RequestException as e:
        print(f"Error sending telegram message: {e}")

def main():
    latest_player = get_latest_player()
    if not latest_player:
        print("Failed to get the latest player.")
        return

    player_identifier = f"{latest_player['id']}:{latest_player['name']}"
    
    last_player_file = 'last_player.txt'
    last_player = ""
    if os.path.exists(last_player_file):
        with open(last_player_file, 'r', encoding='utf-8') as f:
            last_player = f.read().strip()
            
    print(f"Latest player on site: {player_identifier}")
    print(f"Last recorded player : {last_player}")
            
    if player_identifier != last_player:
        print("New player detected! Sending Telegram message...")
        token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        if token and chat_id:
            message = f"🚨 <b>New Player Added!</b>\n\nName: <b>{latest_player['name']}</b>\nLink: https://pesdb.net/efootball/?id={latest_player['id']}"
            send_telegram_message(token, chat_id, message)
            
            with open(last_player_file, 'w', encoding='utf-8') as f:
                f.write(player_identifier)
            print("Successfully updated last_player.txt")
        else:
            print("Telegram secrets not found. Cannot send message.")
            # We still update the file locally so it works without secrets (e.g. testing)
            with open(last_player_file, 'w', encoding='utf-8') as f:
                f.write(player_identifier)
            print("Successfully updated last_player.txt (without sending message)")
    else:
        print("No new players added.")

if __name__ == "__main__":
    main()
