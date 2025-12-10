# Quick Start Guide

Get the Mathematical Question Refinement Chatbot running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Your Groq API Key

Get your free API key from [https://console.groq.com/](https://console.groq.com/)

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY="your-api-key-here"
```

**Windows (CMD):**
```cmd
set GROQ_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export GROQ_API_KEY="your-api-key-here"
```

## Step 3: Start the Backend

```bash
python run_server.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Open the Frontend

1. Open `frontend/index.html` in your web browser, OR
2. Use a simple server:
   ```bash
   cd frontend
   python -m http.server 3000
   ```
   Then open `http://localhost:3000`

## Step 5: Test It!

1. Enter a mathematical question like: "What is the derivative of x squared?"
2. Follow the conversation flow:
   - Validation → Refinement → Accept/Reject → Similarity Check
3. Try an invalid input like "Hello" to see the validation loop

## Troubleshooting

**"GROQ_API_KEY not set" error:**
- Make sure you set the environment variable in the same terminal where you run the server
- Restart the terminal after setting the variable

**"Questions file not found" warning:**
- Ensure `question.json` is in the project root directory
- The similarity check will still work, just with an empty database

**Port 8000 already in use:**
- Change the port in `run_server.py` or use:
  ```bash
  uvicorn backend.main:app --port 8001
  ```

**Frontend can't connect to backend:**
- Make sure the backend is running on `http://localhost:8000`
- Check browser console for CORS errors
- Update `API_BASE_URL` in `frontend/app.js` if using a different port

## Example Conversation

```
You: what is derivitive of x squared

Bot: ✓ Your question is valid! Let's proceed to refinement.

Bot: ✅ Here is the refined version of your question:
     "What is the derivative of x²?"
     📝 Changes made: Fixed spelling, improved formatting, added proper notation

[Accept] [Request Changes]

You: Accept

Bot: Great! Checking for similar questions...
Bot: ✅ No similar questions found. Your question appears to be unique!
```

Enjoy refining your mathematical questions! 🎉

