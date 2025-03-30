from configparser import ConfigParser
from contextlib import asynccontextmanager
import aiosqlite
from fastapi import Depends, FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, Response
import hashlib
from fastapi.responses import StreamingResponse
from htmldocx import HtmlToDocx
from docx import Document
import io
from sqlalchemy.engine import url
from sqlalchemy.orm import Session, session
from cv import CV
from database import SessionLocal, engine
from models import Base , SurveyResponse
import uuid

templates = Jinja2Templates(directory="templates")
Base.metadata.create_all(bind=engine)
app = FastAPI()
app.mount("/static", StaticFiles(directory="templates/static"), name="static")
config = ConfigParser()
config.read("conf.ini")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def serve_form(request: Request, response: Response):
    response = templates.TemplateResponse("index.html", {"request": request})
    return response


@app.post("/submit")
async def submit_survey(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    answers = dict(form_data)

    user_message = f"Данные анкетируемого: {answers}"

    cv = CV()
    ids = cv.run_request(user_message)
    thread_id = ids["thread_id"]
    run_id = ids["run_id"]
    
    result = SurveyResponse(
        answers=str(answers),
        thread_id=thread_id,
        run_id=run_id
    )
    db.add(result)

    db.commit()

    return JSONResponse(content={
        "thread_id": thread_id,
        "run_id": run_id
    })

@app.get("/users")
async def get_responses(request:Request, db: Session = Depends(get_db)):
    auth_cookie = request.cookies.get("auth")
    if auth_cookie != "1":
        return RedirectResponse(url="/login")

    users = db.query(SurveyResponse).all()
    return users

@app.get("/portrait")
async def get_portrait(request: Request , db: Session = Depends(get_db)):
    auth_cookie = request.cookies.get("auth")
    if auth_cookie != "1":
        return RedirectResponse(url="/login")

    answers = db.query(SurveyResponse.answers).all()
    cv = CV()
    portrait = cv.get_portrait(str(answers))
    return templates.TemplateResponse("portrait.html", {
        "request": request,
        "portrait": portrait,
    })


@app.get("/cv/{user_id}")
def get_cv(request: Request, user_id: str, db: Session = Depends(get_db)):

    if not user_id:
        return RedirectResponse(url='/', status_code=303)
        
    thread_run = user_id.split('__')
    user_data = db.query(SurveyResponse).filter(
        SurveyResponse.thread_id == thread_run[0], 
        SurveyResponse.run_id == thread_run[1]).first()

    if not user_data :
        return RedirectResponse(url='/', status_code=303)

    return templates.TemplateResponse("cv.html", {
        "request": request,
        "gpt_answer": user_data.gpt_answer,
        "user_id": user_id
    })


@app.get("/check-status")
async def check_status(thread_id: str, run_id: str, db: Session = Depends(get_db)):
    cv = CV()
    result = cv.get_response(thread_id=thread_id, run_id=run_id)

    if result["answer"]:
        record = db.query(SurveyResponse).filter(
            SurveyResponse.thread_id == thread_id, 
            SurveyResponse.run_id == run_id).first()
        if record:
            record.gpt_answer = result["answer"]
            db.commit()

        return {"answer": result["answer"]}

    return {"answer": None}


@app.get("/download-cv/{user_id}")
async def download_cv(request: Request, user_id: str, db: Session = Depends(get_db)):
    thread_run = user_id.split('__')
    
    record = db.query(SurveyResponse).filter(
        SurveyResponse.thread_id == thread_run[0], 
        SurveyResponse.run_id == thread_run[1]).first()

    if not record or not record.gpt_answer:
        return HTMLResponse("CV не найден в ответе", status_code=400)

    parts = record.gpt_answer.split("<h2>CV:</h2>")
    if len(parts) < 2:
        return HTMLResponse("CV не найден в ответе", status_code=400)

    cv_html = f"<h2>CV:</h2><br>{parts[1]}"

    doc = Document()
    new_parser = HtmlToDocx()
    new_parser.add_html_to_document(cv_html, doc)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=cv.docx"}
    )

@app.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, login: str = Form(...), password: str = Form(...)):
    correct_login = config["USER"]["login"]
    correct_password = config["USER"]["password"]

    if login == correct_login and password == correct_password:
        response = RedirectResponse(url="/portrait", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="auth", value="1", httponly=True)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный логин или пароль"})
