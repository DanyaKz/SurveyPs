from typing import Optional
from openai import OpenAI
import openai
from configparser import ConfigParser
import time
import json

from openai.types.beta.threads.text import Text
from openai.types.beta.threads.text_content_block import TextContentBlock

class CV:
    def __init__(self) -> None:
        self.config = ConfigParser()
        self.config.read("conf.ini")

        self.client = OpenAI(
            api_key = self.config["OPENAI"]["api_key"]
        )
    
    def run_request(self, message) -> dict: 
        completion = self.client.beta.threads.create_and_run(
            assistant_id = self.config["OPENAI"]["assistant_id"],
            thread={
                "messages": [
                    {"role": "user", "content": message}
                ]
            }
            )
        return {"run_id": completion.id, "thread_id": completion.thread_id}

    def get_response(self, thread_id, run_id) -> dict:
        run_status = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

        if run_status.status == "completed": 
            return self.get_last_msg(thread_id=thread_id)

        if run_status.status in {"failed", "cancelled", "expired"}:
            new_run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.config["OPENAI"]["assistant_id"]
            )
            return {
                "answer": None,
                "retry": True,
                "new_run_id": new_run.id
            }

        return {"answer": None}
    
    def get_last_msg(self, thread_id) -> dict:
        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        msg = messages.data[0]
        if msg.content and msg.content[0].type == "text":
            answer = msg.content[0].text.value
        else:
            answer = "Ответ не получен"
        return {"answer": answer}

    def get_portrait(self, answers : str):
        text = """Ты аналитик данных. На ответы пользователей сформируй следующий анализ. Необходимо предоставить средние значения, либо моду, либо по описанию, что является самым частым  по всем участникам. Не раскрывай сами овтеты участников. Отвечай кратко, меня инетересует только отчет и отформатируй ответы , чтобы они не выглядели сухо. Если данные сильно варьируются или нет однозначного ответа , все равно попытайся выбрать самый частый , либо обобщи результат. Не используй markdown , используй для этого html, не переноси строку, но нельзя использовать теги <html>, <body>, для перечисления используй <ul>, <li>. Пункты, на которые ты должен ответить :  
            Возраст
            Гендер
            Сфера специальности обучения
            Наиболее сложные аспекты учебы
            Готовность к работе по специальности
            Наиболее интересные темы, проекты
            Пройденное доп обучение (курсы, тренинги и т.д.)
            Что хотел бы дополнительно изучить (курсы, тренинги т.д.)
            Есть / нет понимание о коучинге
            Был / не был опыт коучинга
            Какой формат коучинга был
            Полезно / не полезно сотрудничество с коучем
            Ожидания по итогам коучинг-сессии
            Оценка своих способностей достигать целей с коучем
            Видение своей карьеры через 3 года после окончания ВУЗа
            Главные цели на 2 года после окончания ВУЗа
            Важные аспекты будущей профессии
            Альтернативные карьерные пути
            Какие организации и профессионалы интересны
            Представление о первом шаге в карьере
            Ресурсы, которые готов вложить в свое развитие
            Сильные стороны личности
            Как справляется с неудачами на профессиональном пути
            Что / кто вдохновляет на достижение целей
            Лидерские качества 
            Стратегии для решения нестандартных задач
            Навыки, которые укрепят уверенность
            Оценка своих навыков в выполнении задач высокой сосредоточенности
            Что вдохновляет на достижение высокого уровня профессионализма
            
        """
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": text},
                {"role": "user", "content": "Ответы пользователей:" + answers},
                    ]
                )
        return response.choices[0].message.content

    

# cv = CV()
# resp = cv.run_request("{'age': '24', 'gender': 'male', 'specialization': 'medical', 'study_difficulties': 'тайм-менеджмент', 'work_readiness': 'medium', 'specialization_factors': 'оаоаоа', 'coaching_knowledge': 'yes', 'courses_taken': 'напиши садам алейкум'}")
# print(resp)
# time.sleep(10)
# a = cv.get_response(thread_id= 'thread_NbtuIWf7H6cpjox5EAhx25Ox', run_id= 'run_LPIXvOJNSlyDqrQ5JCZUYMEq')
# print(a)
# d ={'answer': [TextContentBlock(text=Text(annotations=[], value='Вывод: Выделяется, что для вас важна организация времени, и есть желание применять коучинговые знания. Страхи или сопротивления могут возникать из-за необходимости управлять временными ресурсами. Ваш интерес к медицине устойчив, а понимание коучинга может способствовать более осознанному подходу к карьерному росту. Запланируйте изучение техник тайм-менеджмента. Курсы особенно интересны, и вы проявляете культурное любопытство, что может стать хорошей платформой для расширения кругозора и навыков. Используйте эти ресурсы и амбиции для определения следующего шага в карьере.\n\nCV: {"age": "24", "gender": "male", "specialization": "medical", "study_difficulties": "тайм-менеджмент", "work_readiness": "medium", "specialization_factors": "оаоаоа", "coaching_knowledge": "yes", "courses_taken": "напиши садам алейкум"}'), type='text')]}
# print(json.loads(a["answer"][0].text.value.split('CV:')[1]))
# print(d["answer"][0].text.value.split('CV:')[0])