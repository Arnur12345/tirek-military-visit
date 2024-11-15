from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import google.generativeai as genai

app = FastAPI()

# Enable CORS for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
model = genai.GenerativeModel("gemini-1.5-flash")

# Helper function to analyze answers locally
def analyze_answers(answers):
    positive_responses = sum(1 for answer in answers if answer.lower() in ["yes", "often", "always"])
    negative_responses = len(answers) - positive_responses

    if positive_responses > 6:
        return "The responses indicate a high likelihood of emotional distress or mental health issues."
    elif positive_responses > 3:
        return "There are some indicators of stress or mental health concerns, but the overall state seems moderate."
    else:
        return "The responses suggest a stable mental state with no strong indications of emotional distress."

# Endpoint for questionnaire submission
@app.post("/submit_questionnaire", response_class=JSONResponse)
async def submit_questionnaire(
    question1: str = Form(...),
    question2: str = Form(...),
    question3: str = Form(...),
    question4: str = Form(...),
    question5: str = Form(...),
    question6: str = Form(...),
    question7: str = Form(...),
    question8: str = Form(...),
    question9: str = Form(...),
    question10: str = Form(...)
):
    # Collect answers
    answers = [
        question1, question2, question3, question4, question5,
        question6, question7, question8, question9, question10
    ]

    # Perform local analysis on the answers
    mental_state = analyze_answers(answers)

    # Use Gemini API for additional analysis
    try:
        gemini_prompt = f"Analyze the following responses to assess mental health: {answers}"
        gemini_response = model.generate_content(gemini_prompt)
        gemini_result = gemini_response.text if gemini_response and gemini_response.text else "Gemini analysis unavailable."
    except Exception as e:
        gemini_result = f"Error with Gemini API: {str(e)}"

    # Return combined results
    return JSONResponse(content={
        "mental_state": mental_state,
        "gemini_analysis": gemini_result
    })
