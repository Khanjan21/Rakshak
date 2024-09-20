from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import time
import google.generativeai as genai

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify specific origins for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],   # Allow all headers
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# ... rest of your code ...


# Google AI SDK configuration with hardcoded API key for testing (remove in production)
genai.configure(api_key="AIzaSyD3ts-1DPNF_il5WFqj9RT3AA52TC-oMxY")

# Global variable to hold uploaded files and the model
files = []
model = None

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    try:
        file = genai.upload_file(path, mime_type=mime_type)
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")
        return file
    except Exception as e:
        print(f"Failed to upload file: {e}")
        raise

def wait_for_files_active(files):
    """Waits for the given files to be active."""
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")
    print()

# Chat model setup with Gemini
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Upload files to Gemini when the application starts
try:
    files = [
        upload_to_gemini("vertopal.com_health-data (1).pdf", mime_type="application/pdf"),
    ]
    wait_for_files_active(files)
except Exception as e:
    print(f"Error during file processing: {e}")

# Pydantic model for request validation
class ChatRequest(BaseModel):
    message: str

# API endpoint for receiving user input and sending response
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        user_message = request.message
        print(f"User message: {user_message}")

        # Start the chat session with the model and pass the user message
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        files[0],
                        "Your name is Rakshak, created by Khanjan as a healthcare bot for everyone. If someone asks about Khanjan, simply mention that he is the creator of this bot, designed to provide accessible healthcare assistance. Keep conversations focused on healthcare topics, such as health tips, general medical advice, and reminders for medications or checkups. Avoid discussing any topics outside healthcare and prevent hate speech, offensive language, or sexual discussions from being part of the conversation. Always interact in a friendly and professional manner.",
                    ],
                },
            ]
        )

        # Send the user's message and get a response
        response = chat_session.send_message(user_message)

        # Return chatbot's response as JSON
        return {"text": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Start FastAPI using Uvicorn if this script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
