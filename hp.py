import google.generativeai as genai # type: ignore
from flask import Flask, request, jsonify # type: ignore
import os
from dotenv import load_dotenv # type: ignore
from flask_cors import CORS # type: ignore

# Load API key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("AIzaSyCQSWraJEnFEcdqd1tBrKFDoLjjLCBQAZY"))

app = Flask(__name__)
CORS(app)

@app.route("/analyze", methods=["POST"])
def analyze_resume():
    file = request.files["resume"]
    text = file.read().decode("utf-8")  # Read text from file

    prompt = f"Analyze this resume for job suitability and suggest improvements:\n\n{text}"
    
    # Generate response using Gemini API
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    return jsonify({"analysis": response.text})

if __name__ == "__main__":
    app.run(debug=True)
