from contextlib import asynccontextmanager
import aiosqlite
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, Response
import hashlib

templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with aiosqlite.connect("survey.db") as db:
        await db.execute("PRAGMA journal_mode=WAL;")  
        await db.commit()
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="templates/static"), name="static")


def generate_fingerprint(ip: str, user_agent: str, accept_language: str = ""):
    raw_data = f"{ip}-{user_agent}-{accept_language}"
    return hashlib.sha256(raw_data.encode()).hexdigest()


@app.get("/")
async def serve_form(request: Request, response: Response):
    fingerprint = request.cookies.get("fingerprint")

    if not fingerprint:
        ip = request.client.host # type:ignore
        user_agent = request.headers.get("User-Agent", "unknown")
        accept_language = request.headers.get("Accept-Language", "unknown")

        fingerprint = generate_fingerprint(ip, user_agent, accept_language)
        response.set_cookie(key="fingerprint", value=fingerprint, httponly=True)
    print(fingerprint)
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/submit")
async def submit_survey(request: Request):

    form_data = await request.form()
    answers = dict(form_data)
    session_id = request.client.host # type:ignore

    async with aiosqlite.connect("survey.db") as db:
        await db.execute(
            "INSERT INTO survey_responses (session_id, answers) VALUES (?, ?)",
            (session_id, str(answers))
        )
        await db.commit()

    return templates.TemplateResponse("index.html", {"request": request, "status": "saved"})

@app.get("/responses")
async def get_responses():
    async with aiosqlite.connect("survey.db") as db:
        cursor = await db.execute("SELECT id, session_id, answers, created_at FROM survey_responses")
        rows = await cursor.fetchall()

    return [{"id": row[0], "session_id": row[1], "answers": row[2], "created_at": row[3]} for row in rows]
