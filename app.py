"""AI Study Buddy: paste notes or upload a PDF; get a summary, a 5-question quiz and key terms."""
import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # loads GEMINI_API_KEY from the .env file before the brain is imported
from study_buddy import make_study_pack, read_pdf, save_pack  # noqa: E402

st.set_page_config(page_title="AI Study Buddy")
st.title("AI Study Buddy")
st.caption("Paste your notes or upload a PDF. Get a summary, a 5-question quiz and 3 key terms.")

if not os.getenv("GEMINI_API_KEY"):
    st.error("No API key found. Create a file named .env with the line GEMINI_API_KEY= followed by your key (see README).")
    st.stop()

notes = st.text_area("Your notes", height=200, placeholder="Paste a topic from your notes here")
pdf = st.file_uploader("Or upload a PDF", type="pdf")

if st.button("Make my study pack", type="primary"):
    if pdf is not None:
        notes = read_pdf(pdf)
        if not notes:
            st.error("This PDF has no readable text (it may be a scanned image). Paste the text instead.")
            st.stop()
    if len(notes.strip()) < 50:
        st.warning("Please give at least a few sentences of notes.")
        st.stop()
    with st.spinner("Your study buddy is reading..."):
        try:
            pack = make_study_pack(notes)
        except RuntimeError as error:
            st.error(str(error))
            st.stop()
    st.session_state.pack = pack
    st.session_state.saved_to = str(save_pack(pack))

pack = st.session_state.get("pack")
if pack:
    st.header(pack.title)

    st.subheader("Summary")
    for point in pack.summary:
        st.markdown(f"- {point}")

    st.subheader("Quiz")
    for number, mcq in enumerate(pack.mcqs, start=1):
        choice = st.radio(f"Q{number}. {mcq.question}", mcq.options, index=None, key=f"q{number}")
        if choice is not None:
            if choice == mcq.answer:
                st.success("Correct!")
            else:
                st.error(f"Not quite. The answer is: {mcq.answer}")
        with st.expander("Explanation"):
            st.write(mcq.explanation)

    st.subheader("Key terms")
    for item in pack.key_terms:
        st.markdown(f"**{item.term}**: {item.meaning}")

    st.caption(f"Saved to {st.session_state.saved_to}")
