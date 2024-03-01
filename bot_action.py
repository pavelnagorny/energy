import requests


def send_message(token, chat_id, message):
    telegram_api_url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Prepare the payload
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(telegram_api_url, data=payload, verify=False)

    if response.status_code == 200:
        print("Message sent successfully.")
    else:
        print("Failed to send the message. Status code:", response.status_code)
