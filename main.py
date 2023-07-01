from telethon.sync import TelegramClient
import openai
from dotenv import load_dotenv
import os
import time

load_dotenv()


class Telegram_Commentator:
    def __init__(self):
        # замените список тегов каналов на свой список
        self.channels: list = ['energynewz', 'militaryZmediaa', 'novosti_ru_24', 'voenacher']
        openai.api_key = os.getenv("OpenAI_token")
        self.api_id: int = os.getenv('Api_id')
        self.api_hash: str = os.getenv('Api_hash')
        self.owner_ID: str = os.getenv('Owner_id')
        self.client = None

    def start_telegram_client(self):
        # запуск сессии телеграмма
        self.client = TelegramClient('session_name', self.api_id, self.api_hash)
        self.client.start()

    def write_comments_in_telegram(self):
        """
			Чтобы не было бесконечного
			спама под одним и тем же постом,
			сделано сохранение айди поста
			"""
        last_message_ids = {name: 0 for name in self.channels}
        # перебираем каналы по списку
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
                    # сохраняем айди поста
                    if post.id != last_message_ids[name]:
                        last_message_ids[name] = post.id
                        """
                        генерируем коммент,
			            промпт можете адаптировать под себя
			            """
                        prompt = "Вы патриот России и девушка, вам нужно написать осмысленный человекоподобный яркий комментарий до 11 слов к посту: " + post.raw_text
                        output = openai.Completion.create(
                            engine='text-davinci-003',
                            prompt=prompt,
                            max_tokens=170,
                            temperature=0.4,
                            n=1,
                            stop=None
                        )
                        if output.choices:
                            output = output.choices[0].text.strip()
                            # openAi иногда возвращает пустой текст
                            if output == "":
                                output = "Даже не знаю, что тут сказать...."
                        else:
                            output = "Даже не знаю, что тут сказать...."
                        try:
                            # задержка для избежания бана модерами канала
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
                            # сделано для избежания чрезмерного спама
                            time.sleep(25)

    def run(self):
        # запуск и цикл вынесены отдельно для удобства
        self.start_telegram_client()
        while True:
            self.write_comments_in_telegram()


# запускаем наше чудо
AI_commentator = Telegram_Commentator()
AI_commentator.run()