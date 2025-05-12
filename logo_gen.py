import requests
import random
import time
import base64
import os
from token_manager import get_valid_token
import config as cfg

def generate_logo(forma, style, description):
    prompt = f"Нарисуй логотип в форме {forma}, стиль: {style}, описание: {description}"
    return generate_by_prompt(prompt, output_path=None)

def generate_by_prompt(prompt, output_path=None):
    iam_token = get_valid_token()
    headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json"
    }
    data = {
        "modelUri": f"art://{cfg.catalog_id}/yandex-art/latest",
        "generationOptions": {
            "seed": f"{random.randint(0, 1000000)}",
            "aspectRatio": {"widthRatio": "1", "heightRatio": "1"}
        },
        "messages": [{"weight": "1", "text": prompt}]
    }

    try:
        response = requests.post(cfg.url_1, headers=headers, json=data)
        response.raise_for_status()
        request_id = response.json()['id']
    except Exception as e:
        return f"Ошибка при отправке запроса: {e}"

    for _ in range(30):
        try:
            result = requests.get(f"{cfg.url_2}/{request_id}", headers={"Authorization": f"Bearer {iam_token}"})
            result.raise_for_status()
            result_json = result.json()
            if result_json.get("done", False):
                image_base64 = result_json["response"]["image"]
                image_data = base64.b64decode(image_base64)
                if not output_path:
                    os.makedirs('static/generated', exist_ok=True)
                    output_path = os.path.join('static/generated', f'image_{int(time.time())}.jpeg')
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                return output_path
        except Exception:
            pass
        time.sleep(3)

    return "Ошибка: Истекло время ожидания генерации изображения."
