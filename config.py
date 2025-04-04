from dotenv import load_dotenv
import os


class Config: 
    def __init__(self):
        load_dotenv()

        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
        self.LOGIN_USER = os.getenv("LOGIN_USER")
        self.LOGIN_PASSWORD_HASH = os.getenv("LOGIN_PASSWORD_HASH")
        self.DATABASE_URL = os.getenv("DATABASE_URL")
