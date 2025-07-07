
import streamlit as st
from google.generativeai import GenerativeModel
import google.generativeai as genai
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

# ---- Initialize Gemini ----
genai.configure(api_key="AIzaSyDllowP3b5Q6zzRQmJBqPuKrHRF-8pgrcM")  # Replace with your Gemini API key
model = GenerativeModel('gemini-1.5-flash')

# ---- Streamlit Config ----
st.set_page_config(page_title="Code Explainer 🚀", page_icon="💡")

st.title("🔍 Code_Explainer")
st.write("Turn complex code into clear concepts — in your own language!")

# ---- Session State for History ----
if "history" not in st.session_state:
    st.session_state.history = []

# ---- File Upload ----
uploaded_file = st.file_uploader("📂 Or upload a code file:", type=["py", "js", "java", "cpp", "c", "html", "css"])

code_input = ""

if uploaded_file is not None:
    code_bytes = uploaded_file.read()
    code_input = code_bytes.decode("utf-8")
    st.success(f"✅ Uploaded `{uploaded_file.name}` successfully!")

# ---- Or manual input ----
code_input_manual = st.text_area("📄 Or paste your code here:", height=200)

# If both uploaded and manual, uploaded takes priority
if not code_input:
    code_input = code_input_manual

# ---- Language options ----
languages = [
    "Auto-Detect",
    "Python", "JavaScript", "C++", "Java", "C", "HTML", "CSS",
]

selected_lang_detect = st.selectbox("💡 Auto-detect or select code language:", languages)

# ---- Explanation language ----
explanation_languages = [
    "English", "Hindi", "Tamil", "Telugu", "Kannada", "Bengali",
    "Gujarati", "Marathi", "Punjabi", "Urdu", "Spanish",
    "French", "German", "Mandarin", "Japanese"
]

selected_explanation_language = st.selectbox("🌍 Explanation output language:", explanation_languages)

# ---- Explain & Quiz ----
if st.button("🔍 Explain My Code & Make Quiz"):
    if not code_input.strip():
        st.warning("⚠️ Please upload or paste some code first!")
    else:
        with st.spinner("🧠 Gemini is analyzing..."):

            # Auto-detect or use selected
            if selected_lang_detect == "Auto-Detect":
                detect_prompt = (
                    f"Detect the programming language of this code:\n\n"
                    f"{code_input}\n\n"
                    f"Only reply with the language name."
                )
                try:
                    detect_response = model.generate_content(detect_prompt)
                    detected_language = detect_response.text.strip().split("\n")[0]
                except:
                    detected_language = "Unknown"
            else:
                detected_language = selected_lang_detect

            # Explanation Prompt
            explain_prompt = (
                f"You are an expert code explainer.\n"
                f"Explain the following {detected_language} code step-by-step in {selected_explanation_language}:\n\n"
                f"```{detected_language.lower()}\n{code_input}\n```\n"
                f"Keep it simple, clear, and helpful for beginners."
            )

            # Quiz Prompt
            quiz_prompt = (
                f"Generate 3 short quiz questions (with answers) "
                f"to test understanding of the following {detected_language} code.\n\n"
                f"Code:\n{code_input}\n\n"
                f"Language: {selected_explanation_language}."
            )

            try:
                # Get explanation
                explanation = model.generate_content(explain_prompt).text

                # Get quiz
                quiz = model.generate_content(quiz_prompt).text

                # Save to session state
                st.session_state.history.append({
                    "code": code_input,
                    "language": detected_language,
                    "explanation_lang": selected_explanation_language,
                    "explanation": explanation,
                    "quiz": quiz
                })

                # Output
                st.subheader("✅ Detected Language:")
                st.write(f"**{detected_language}**")

                st.subheader("📘 Explanation:")
                st.markdown(explanation)

                st.subheader("📌 Original Code:")
                st.code(code_input, language=detected_language.lower())

                st.subheader("🧩 Practice Quiz:")
                st.markdown(quiz)

                # ---- Downloads ----
                col1, col2 = st.columns(2)
                txt = f"Code:\n{code_input}\n\nDetected Language: {detected_language}\n\nExplanation:\n{explanation}\n\nQuiz:\n{quiz}"

                with col1:
                    st.download_button(
                        "⬇️ Download as TXT",
                        data=txt,
                        file_name="code_explanation_quiz.txt",
                        mime="text/plain"
                    )

                with col2:
                    pdf_output = BytesIO()
                    c = canvas.Canvas(pdf_output, pagesize=A4)
                    c.setFont("Helvetica", 12)

                    text_object = c.beginText()
                    text_object.setTextOrigin(inch, 11 * inch)
                    text_object.setFont("Helvetica", 12)

                    for line in txt.split('\n'):
                        text_object.textLine(line)

                    c.drawText(text_object)
                    c.showPage()
                    c.save()
                    pdf_output.seek(0)

                    st.download_button(
                        "⬇️ Download as PDF",
                        data=pdf_output,
                        file_name="code_explanation_quiz.pdf",
                        mime="application/pdf"
                    )

            except Exception as e:
                st.error(f"❌ Oops! Something went wrong: {e}")

# ---- History Sidebar ----
with st.sidebar:
    st.header("📚 History")
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-5:]), 1):
            st.write(f"**#{len(st.session_state.history) - i + 1}** ({item['language']} ➜ {item['explanation_lang']})")
            st.code(item['code'][:100] + "..." if len(item['code']) > 100 else item['code'],
                    language=item['language'].lower())
            with st.expander("Explanation"):
                st.markdown(item['explanation'])
            with st.expander("Quiz"):
                st.markdown(item['quiz'])
    else:
        st.info("Your explanations & quizzes will appear here!")
