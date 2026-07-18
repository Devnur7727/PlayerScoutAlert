import os
import requests
from bs4 import BeautifulSoup

def get_players_on_page():
    url = "https://pesdb.net/efootball/?all=1&sort=time_added"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching pesdb: {e}")
        return []
        
    soup = BeautifulSoup(response.text, 'html.parser')
    players = []
    
    for a_tag in soup.find_all('a'):
        href = a_tag.get('href', '')
        if '?id=' in href:
            try:
                player_id = href.split('?id=')[1].split('&')[0]
                player_name = a_tag.text.strip()
                if player_name and player_id.isdigit():
                    players.append({'id': player_id, 'name': player_name})
            except IndexError:
                continue
    
    return players

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
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
    players_on_page = get_players_on_page()
    if not players_on_page:
        print("Failed to get players from the page.")
        return
    
    last_player_file = 'last_player.txt'
    last_player = ""
    if os.path.exists(last_player_file):
        with open(last_player_file, 'r', encoding='utf-8') as f:
            last_player = f.read().strip()
            
    print(f"Last recorded player: {last_player}")
    
    new_players = []
    for player in players_on_page:
        player_identifier = f"{player['id']}:{player['name']}"
        if player_identifier == last_player:
            # We reached the player we already know about
            break
        new_players.append(player)
        
    if not new_players:
        print("No new players added.")
        return
        
    print(f"Found {len(new_players)} new player(s)!")
    
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if token and chat_id:
        message = f"🚨 <b>{len(new_players)} New Player(s) Added!</b>\n\n"
        for i, p in enumerate(new_players):
            if i >= 30: # Limit to 30 to avoid Telegram message length limits
                message += f"\n<i>...and {len(new_players) - 30} more!</i>"
                break
            message += f"• <b>{p['name']}</b> - <a href='https://pesdb.net/efootball/?id={p['id']}'>View</a>\n"
            
        send_telegram_message(token, chat_id, message)
    else:
        print("Telegram secrets not found. Cannot send message.")

    # Update last_player.txt with the newest player (the first one in the list)
    newest_player = new_players[0]
    newest_identifier = f"{newest_player['id']}:{newest_player['name']}"
    
    with open(last_player_file, 'w', encoding='utf-8') as f:
        f.write(newest_identifier)
    print("Successfully updated last_player.txt")

if __name__ == "__main__":
    main()
