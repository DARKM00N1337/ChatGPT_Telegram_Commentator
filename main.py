from telethon.sync import TelegramClient
import requests
from dotenv import load_dotenv
import os
import time
import json

load_dotenv()

class Telegram_Commentator:
    def __init__(self):
        self.channels: list = ['energynewz', 'militaryZmediaa', 'novosti_ru_24', 'voenacher']
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_id: int = os.getenv('Api_id')
        self.api_hash: str = os.getenv('Api_hash')
        self.owner_ID: str = os.getenv('Owner_id')
        self.client = None
        self.your_site_url = "https://your-site-url.com"  # Замените на URL вашего сайта
        self.your_site_name = "Your Site Name"  # Замените на название вашего сайта

    def start_telegram_client(self):
        self.client = TelegramClient('session_name', self.api_id, self.api_hash)
        self.client.start()

    def generate_comment(self, post_text):
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "HTTP-Referer": self.your_site_url,
            "X-Title": self.your_site_name,
            "Content-Type": "application/json"
        }
        data = {
            "model": "openai/gpt-4-turbo-preview",  # Можете выбрать другую модель
            "messages": [
                {
                    "role": "system",
                    "content": "Вы патриот России и девушка. Пишите осмысленные человекоподобные яркие комментарии до 11 слов."
                },
                {
                    "role": "user",
                    "content": f"Напишите комментарий к этому посту: {post_text}"
                }
            ]
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            else:
                return "Даже не знаю, что тут сказать...."
        except Exception as e:
            print(f"Ошибка при генерации комментария: {e}")
            return "Даже не знаю, что тут сказать...."

    def write_comments_in_telegram(self):
        last_message_ids = {name: 0 for name in self.channels}
        for name in self.channels:
            try:
                channel_entity = self.client.get_entity(name)
            except ValueError as e:
                self.client.send_message(f'{self.owner_ID}', f"Ошибка при получении информации о канале '{name}': {e}")
                print("Ошибка, проверьте личные сообщения!")
                continue
            messages = self.client.get_messages(channel_entity, limit=1)
            if messages:
                for post in messages:
                    if post.id != last_message_ids[name]:
                        last_message_ids[name] = post.id
                        output = self.generate_comment(post.raw_text)
                        try:
                            time.sleep(25)
                            self.client.send_message(entity=name, message=output, comment_to=post.id)
                            self.client.send_message(f'{self.owner_ID}',
                                                     f'Комментарий отправлен!\nСсылка на пост: <a href="https://t.me/{name}/{post.id}">{name}</a>\nСам пост: {post.raw_text[:90]}\nНаш коммент: {output}',
                                                     parse_mode="html")
                            print('Успешно отправлен коммент, проверьте личные сообщения')
                        except Exception as e:
                            self.client.send_message(f'{self.owner_ID}',
                                                     f"Ошибка при отправке комментария в канал '{name}': {e}")
                            print('Ошибка, проверьте личные сообщения')
                        finally:
                            time.sleep(25)

    def run(self):
        self.start_telegram_client()
        while True:
            self.write_comments_in_telegram()

# запускаем наше чудо
AI_commentator = Telegram_Commentator()
AI_commentator.run()
