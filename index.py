from flask import Flask, request, jsonify
from spellchecker import SpellChecker
import re
import PyPDF2

app = Flask(__name__)

def read_cv(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def refine_text(text):
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'http\S+', '', text)
    return text

def check_spelling(text):
    spell = SpellChecker()
    text = refine_text(text)
    words = re.findall(r'\b[a-z]+\b', text)
    misspelled = spell.unknown(words)
    return list(misspelled)

def check_sections(text):
    missing_sections = []
    if not re.search(r'Education', text, re.IGNORECASE):
        missing_sections.append('Education')
    if not re.search(r'Skills', text, re.IGNORECASE):
        missing_sections.append('Skills')
    if not re.search(r'Experience', text, re.IGNORECASE):
        missing_sections.append('Experience')
    if not re.search(r'Certificates', text, re.IGNORECASE):
        missing_sections.append('Certificates')
    if not re.search(r'Languages', text, re.IGNORECASE):
        missing_sections.append('Languages')
    return missing_sections

def generate_feedback(misspelled_words, missing_sections, skills):
    feedback_dict = {"positive_feedback": [], "negative_feedback": [], "career_suggestion": ""}

    if misspelled_words:
        feedback_dict["negative_feedback"].append("Spelling errors found: " + ", ".join(misspelled_words))
    else:
        feedback_dict["positive_feedback"].append("No spelling errors found. Great job!")

    if missing_sections:
        feedback_dict["negative_feedback"].append("You should add more field in your CV like: " + ", ".join(missing_sections))

    if len(missing_sections) <= 2:
        feedback_dict["positive_feedback"].append("Your CV looks good. Well done!")
    else:
         feedback_dict["negative_feedback"].append("You should add more field in your CV")
    # Career suggestion based on skills
    if skills:
        career_suggestion = suggest_career(skills)
        feedback_dict["career_suggestion"] = career_suggestion

    return feedback_dict

def suggest_career(skills):
    skill_career_mapping = {
        "programming": "Software Developer",
    }

    suggested_careers = [skill_career_mapping[skill] for skill in skills if skill in skill_career_mapping]
    return ", ".join(suggested_careers)

@app.route('/upload', methods=['POST'])
def upload_cv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file and file.filename.endswith(".pdf"):
        cv_text = read_cv(file)
        misspelled_words = check_spelling(cv_text)
        missing_sections = check_sections(cv_text)

        # Extracting skills (you can enhance this based on your specific use case)
        skills = ["programming", "communication", "leadership"]  # Placeholder, replace with actual skills extraction logic

        feedback_dict = generate_feedback(misspelled_words, missing_sections, skills)
        return jsonify({"feedback": feedback_dict})
    else:
        return jsonify({"error": "Invalid file format. Please upload a PDF file"})

if __name__ == '__main__':
    app.run(debug=True)
