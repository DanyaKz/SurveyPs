from contextlib import asynccontextmanager
import aiosqlite
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with aiosqlite.connect("survey.db") as db:
        await db.execute("PRAGMA journal_mode=WAL;")  
        await db.commit()
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="templates/static"), name="static")

@app.get("/")
async def serve_form(request: Request):
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
