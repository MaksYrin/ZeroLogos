import requests
import time
import json
import os
from datetime import datetime

# 🔐 Твой OAuth-токен
OAUTH_TOKEN = "y0__xCMz5wUGMHdEyCLnu_7Ep9xmCvuKobbDb4x2qCk3Xz-wpqO"

# 📁 Куда сохраняется IAM-токен
TOKEN_PATH = "generated/iam_token.json"

def update_iam_token():
    try:
        # Убедимся, что папка существует
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)

        url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
        headers = {"Content-Type": "application/json"}
        data = {"yandexPassportOauthToken": OAUTH_TOKEN}

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        iam_token = response.json().get("iamToken")
        expires_at = response.json().get("expiresAt")

        # Сохраняем в файл
        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            json.dump({"iam_token": iam_token, "expires_at": expires_at}, f, indent=2)

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ IAM-токен успешно обновлён.")
        return iam_token

    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Ошибка при обновлении IAM-токена: {e}")
        return None

# 🔁 Запускаем обновление каждый час
if __name__ == "__main__":
    while True:
        update_iam_token()
        time.sleep(3600)  # Обновление каждый час
