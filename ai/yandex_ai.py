import asyncio
from dotenv import load_dotenv
from yandex_cloud_ml_sdk import AsyncYCloudML  # Предполагаем, что SDK имеет асинхронный клиент
from yandex_cloud_ml_sdk.search_indexes import TextSearchIndexType
import os, time
import random
import aiofiles  # Для асинхронной работы с файлами


load_dotenv()

sdk = AsyncYCloudML(  # Используем асинхронный клиент
    folder_id=os.getenv("YANDEX_FOLDER_ID"),
    auth=os.getenv("YANDEX_API_KEY"),
)

class Analyzer:
    def __init__(self) -> None:
        pass
            
    async def init(self, system_prompt: str = None, path: str = None, base: bool = True, memory=None):
        if system_prompt and path:
            raise ValueError("Должен быть указан только один из параметров: text или path")
        self.path = path
        self.system_prompt = system_prompt
        self.base = base
        self.id_model = None
        self.memory = [] if memory else memory
        self.status_memory = memory
        self.message_count = 0

        if not base:
            self.name = "temp/" + ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10)) + '.txt'

            async with aiofiles.open(self.name, 'w', encoding='UTF-8') as f:
                await f.write(system_prompt)
            file = await sdk.files.upload(self.name)  # Предполагаем наличие асинхронного метода
            operation = await sdk.search_indexes.create_deferred([file], index_type=TextSearchIndexType())
            text_index = await operation.wait()
            text_tool = sdk.tools.search_index(text_index)
            model = sdk.models.completions("yandexgpt", model_version="rc")
            assistant = await sdk.assistants.create(model, tools=[text_tool])  # Асинхронное создание ассистента
            self.id_model = assistant.id
        return self
    
    def clear(self):
        self.message_count = 0
        self.memory = [] if self.status_memory else self.status_memory

    async def question(self, query: str, model="yandexgpt"):
        """Асинхронный вопрос к модели"""
        self.message_count += 1
        if self.base:
            answ = await self.question_base(query, model)
        else:
            answ = await self.question_prepared_text(query)
        return answ

    async def question_prepared_text(self, query):
        assistant = await sdk.assistants.get(self.id_model)  # Асинхронное получение ассистента
        text_index_thread = await sdk.threads.create()  # Асинхронное создание потока
        await text_index_thread.write(query)  # Асинхронная запись в поток
        run = await assistant.run(text_index_thread)  # Асинхронный запуск
        result = await run.wait()  # Асинхронное ожидание результата
        answer = " ".join(part for part in result.message.parts)
        return answer
    
    async def question_base(self, query, model):
        model = sdk.models.completions(model, model_version='rc')
        model.configure(temperature=0.5)  # Асинхронная конфигурация

        messages = self.memory or [
            {'role': 'system', 'text': self.system_prompt},
            {'role': 'user', 'text': query},
        ]

        if self.memory is not None:
            messages = self.memory + [{'role': 'user', 'text': query}]

        operation = await model.run_deferred(messages)  # Асинхронный запуск
        result = await operation.wait()  # Асинхронное ожидание
        if self.memory is not None:
            self.memory.append({'role': 'assistant', 'text': result.text})
        return result.text

class Psychologist(Analyzer):
    def __init__(self):
        super().__init__()
        
    async def init(self):
        return await super().init(
            system_prompt="Ты — психолог для поступающего в вуз. Помоги мне и окажи сеанс психотерапии.",
            memory=True
        )
    
    async def user_ask(self, prompt):
        return await self.question(prompt)


async def test():
    ai = await Analyzer().init("Представь, что ты школьный преподаватель и должен составить мне расписание обучения. Я учусь в школе до определённого времени каждый день, но мне надо готовиться к экзаменами. Я укажу сколько часов мне на это требуется за неделю. Твоя задача распределить. Также я ложусь в определённое время и трачу определённое время на дорогу домой. ",base=False)
    print(await ai.question("Я хочу заниматься математикой 3 часа в неделю, 7 часов русским, 4 информатикой. Я заканчиваю обучение в школе в 15:00, еду домой час. Предложи мне расписание на неделю с учётом небольшого отдыха, учти, что я ложусь в 12 вечера."
    ))

if __name__ == '__main__':
    asyncio.run(test())