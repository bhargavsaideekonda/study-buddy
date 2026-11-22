"""The brain of AI Study Buddy: read notes, ask Gemini for a study pack, save it."""
import os
from datetime import datetime
from pathlib import Path

from google import genai
from pydantic import BaseModel
from pypdf import PdfReader

# Tried in order: your own choice from .env first, then a fast model, then a free lite model.
MODELS = [m for m in (os.getenv("GEMINI_MODEL"), "gemini-3.8-flash", "gemini-3.1-flash-lite") if m]
SAVE_FOLDER = Path("saved_packs")
MAX_CHARACTERS = 30000  # keeps very long notes within one request


class MCQ(BaseModel):
    question: str
    options: list[str]
    answer: str
    explanation: str


class KeyTerm(BaseModel):
    term: str
    meaning: str


class StudyPack(BaseModel):
    title: str
    summary: list[str]
    mcqs: list[MCQ]
    key_terms: list[KeyTerm]


PROMPT = """You are a friendly study buddy for a first-year engineering student.
Read the study material below and return:
- title: a short title for the topic
- summary: 5 or 6 short bullet points in simple English
- mcqs: exactly 5 multiple-choice questions, each with 4 options, the correct answer
  copied exactly from the options, and a one-line explanation
- key_terms: exactly 3 important terms, each with a one-line meaning
Use only the study material. Do not add facts that are not in it.

Study material:
{notes}"""


def read_pdf(file) -> str:
    """Return all the text in a PDF (empty if it is only scanned images)."""
    reader = PdfReader(file)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def make_study_pack(notes: str, client=None) -> StudyPack:
    """Ask Gemini for a study pack. Tries each model in MODELS until one answers."""
    client = client or genai.Client()  # reads GEMINI_API_KEY from the environment
    prompt = PROMPT.format(notes=notes[:MAX_CHARACTERS])
    config = {"response_mime_type": "application/json", "response_schema": StudyPack}
    last_error = None
    for model in MODELS:
        try:
            response = client.models.generate_content(model=model, contents=prompt, config=config)
            return StudyPack.model_validate_json(response.text)
        except Exception as error:  # wrong model name, quota used up, network problem...
            last_error = error
    raise RuntimeError(f"Gemini could not make a study pack. Last error: {last_error}")


def save_pack(pack: StudyPack) -> Path:
    """Save the pack as a JSON file, so you can revise from it later."""
    SAVE_FOLDER.mkdir(exist_ok=True)
    path = SAVE_FOLDER / f"{datetime.now():%Y-%m-%d_%H-%M-%S}.json"
    path.write_text(pack.model_dump_json(indent=2), encoding="utf-8")
    return path
