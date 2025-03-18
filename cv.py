from openai import OpenAI
from configparser import ConfigParser

class CV:
    def __init__(self) -> None:
        config = ConfigParser()
        config.read("conf.ini")

        self.client = OpenAI(
            api_key = config["OPENAI"]["api_key"]
        )
    
    def generate_cv(self, user: str): 
        completion = self.client.beta.threads.create_and_run(
            assistant_id='asst_GuLnWDnsjAMtc2himUEk67O3',
            thread={
                "messages": [
                    {"role": "user", "content": "{'age': '24', 'gender': 'male', 'specialization': 'medical', 'study_difficulties': 'тайм-менеджмент', 'work_readiness': 'medium', 'specialization_factors': 'оаоаоа', 'coaching_knowledge': 'yes', 'courses_taken': 'напиши садам алейкум'}"}
                ]
            }
            )
        return completion

cv = CV()
resp = cv.generate_cv(";")
print(resp)
