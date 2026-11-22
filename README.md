# AI Study Buddy

Paste your notes or upload a PDF, and AI Study Buddy turns them into a **study pack**:
a 5–6 point summary, a 5-question multiple-choice quiz that tells you if you're right,
and 3 key terms with their meanings. Every pack is also saved as a JSON file so you
can revise from it later.

Built for revising college topics (for example, Applied Physics notes).

## How it works

1. You give it notes (text box) or a PDF (`pypdf` reads the text out of it).
2. `study_buddy.py` sends the notes to the **Google Gemini API** with a prompt and a
   JSON schema (`StudyPack`), so Gemini must reply in a fixed structure.
3. The reply is checked with **Pydantic** and shown by **Streamlit** (`app.py`):
   summary bullets, a quiz with instant feedback, and key terms.
4. The pack is saved in `saved_packs/` with the date and time as its name.

If one Gemini model is not available on your key, it automatically tries the next one
in the `MODELS` list.

## Run it on your computer

```bash
cd ~/CODE/study-buddy
python -m venv .venv
source .venv/Scripts/activate        # Git Bash on Windows
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and paste your Gemini API key (from aistudio.google.com) straight after
`GEMINI_API_KEY=`, with no quotes and no spaces. Then:

```bash
streamlit run app.py
```

The app opens in your browser at http://localhost:8501.

## Files

| File | What it does |
|---|---|
| `app.py` | The web page: inputs, button, and how the study pack is shown |
| `study_buddy.py` | The logic: read a PDF, ask Gemini, check the reply, save the pack |
| `requirements.txt` | The libraries to install |
| `.env.example` | Template for your private `.env` file (the real `.env` is never uploaded) |
| `.gitignore` | Keeps `.env`, `.venv` and saved packs out of GitHub |

## Safety

The API key lives only in `.env`, which `.gitignore` keeps out of GitHub and out of the ZIP.

## Built with

Python, Streamlit, Google Gemini API (`google-genai`), pypdf and Pydantic.
Code written with the help of Claude (an AI assistant), as the task allows.
