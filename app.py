import google.generativeai as genai  # Google AI API
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from flask_cors import CORS
import pdfminer.high_level  # Extract text from PDFs
from docx import Document  # Extract text from DOCX files
from io import BytesIO

# Load API keys from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# Ensure API key is loaded correctly
if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY is missing. Check your .env file.")

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Instead of restricting to just `/analyze`



@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Flask server is running! 🚀"}), 200

def extract_text(file):
    """Extract text from a PDF or DOCX resume."""
    try:
        filename = file.filename.lower()
        file_bytes = BytesIO(file.read())  # Read file into memory
        file.seek(0)  # Reset file cursor

        if filename.endswith(".pdf"):
            return pdfminer.high_level.extract_text(file_bytes).strip()
        elif filename.endswith(".docx"):
            doc = Document(file_bytes)
            return "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])
        else:
            return None  # Unsupported file type
    except Exception as e:
        print(f"❌ Error extracting text: {str(e)}")
        return None

@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return jsonify({"error": "Resume file is required"}), 400

    file = request.files["resume"]

    # Validate file format before processing
    if not (file.filename.endswith(".pdf") or file.filename.endswith(".docx")):
        return jsonify({"error": "Only PDF and DOCX formats are supported"}), 400

    resume_text = extract_text(file)

    if not resume_text:
        return jsonify({"error": "Could not extract text from the resume"}), 400

    prompt = f"Analyze this resume for job suitability and suggest improvements:\n\n{resume_text}"

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)

        if not response or not response.text.strip() or not hasattr(response, 'text'):
            return jsonify({"error": "AI response is empty. Try again later."}), 500

        return jsonify({"response": response.text.strip()})
    except Exception as e:
        print(f"❌ AI API Error: {str(e)}")
        return jsonify({"error": "Failed to process resume. Try again later."}), 500

if __name__ == "__main__":
    app.run(debug=True)
