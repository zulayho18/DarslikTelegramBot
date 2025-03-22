import requests
from config import BASE_URL


def user_create(chat_id: str, username: str, full_name: str):
    user = {
        "chat_id": chat_id,
        "username": f"@{username}" if username else None,
        "full_name": full_name
    }

    print("Yuborilayotgan ma'lumot:", user)  # 👈 Konsolga chop etish

    try:
        response = requests.post(
            url=f"{BASE_URL}/bot-users/", json=user, headers={"Content-Type": "application/json"}
        )
        print("API javobi:", response.text)  # 👈 API'dan kelgan xabarni chop etish
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"user_create xatolik: {e}")
        return None
