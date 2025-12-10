# Mathematical Question Refinement Chatbot

A complete chatbot application that helps users refine their mathematical questions through validation, refinement, and similarity checking using LangChain, Groq API, and semantic embeddings.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Architecture & Design](#architecture--design)
- [Troubleshooting](#troubleshooting)

```bash
pip install -r requirements.txt
```

This command reads `requirements.txt` and installs all packages listed in it. For this project, it installs:
- **FastAPI** & **Uvicorn** - Web framework and server
- **LangChain** & **LangChain-Groq** - LLM integration with Groq API
- **SentenceTransformers** & **FAISS** - For semantic similarity search
- **Pydantic** - Data validation
- And other supporting packages

**Yes, this project uses requirements.txt** - it's essential for installing all dependencies.

## Features

1. **User Input Phase**: Chatbot prompts for a mathematical question
2. **Validation Loop**: Validates if input is a valid mathematical question using LangChain + Groq
   - Loops until a valid question is provided
   - Provides helpful suggestions for invalid inputs
3. **Refinement Phase**: Refines questions for grammar, clarity, and formatting
   - Preserves mathematical meaning
   - User can accept or request changes
   - Feedback loop continues until user confirms
4. **Similarity Check**: Finds semantically similar questions using embeddings
   - Uses FAISS + SentenceTransformers
   - 80% similarity threshold
   - Displays similar questions with scores
5. **Interactive UI**: Clean chat interface with conversation history

## Project Structure

```
mathematical_question-refinement-chatbot/
├── backend/
│   ├── main.py                    # FastAPI application
│   └── services/
│       ├── validation_service.py  # Validates mathematical questions
│       ├── refinement_service.py  # Refines questions
│       └── similarity_service.py  # Finds similar questions
│
├── frontend/
│   ├── index.html                 # Chat interface
│   ├── styles.css                 # Styling
│   └── app.js                     # Frontend logic
│
├── question.json                  # Sample questions database
├── requirements.txt               # Python dependencies (IMPORTANT!)
├── run_server.py                  # Server startup script
└── test_imports.py                # Test script
```

## Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages listed in `requirements.txt`.

### Step 2: Get Groq API Key

1. Sign up at [https://console.groq.com/](https://console.groq.com/)
2. Generate an API key from the dashboard

### Step 3: Set Environment Variable

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

### Step 4: Start Backend Server

```bash
python run_server.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 5: Open Frontend

**Option A:** Open `frontend/index.html` directly in your browser

**Option B (Recommended):** Use a simple server:
```bash
cd frontend
python -m http.server 3000
```
Then open `http://localhost:3000` in your browser

### Step 6: Test It!

1. Enter a mathematical question: `"What is the derivative of x squared?"`
2. Follow the flow: Validation → Refinement → Accept/Reject → Similarity Check
3. Try invalid input: `"Hello"` to see validation loop

## Detailed Setup

### Prerequisites

- **Python 3.8+** - Check with `python --version`
- **Groq API Key** - Free account at [console.groq.com](https://console.groq.com/)

### Installation Steps

1. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   This installs:
   - FastAPI & Uvicorn (web framework)
   - LangChain & LangChain-Groq (LLM integration)
   - SentenceTransformers & FAISS (similarity search)
   - Pydantic, NumPy, and other dependencies

2. **Verify Installation:**
   ```bash
   python test_imports.py
   ```
   
   Expected output:
   - [OK] for file structure
   - [OK] for JSON structure
   - [FAIL] for imports (if dependencies not installed yet)

3. **Set API Key:**
   - See Step 3 in Quick Start above
   - Make sure to set it in the same terminal where you'll run the server

4. **Start Server:**
   ```bash
   python run_server.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Open Frontend:**
   - See Step 5 in Quick Start above

## Usage Guide

### Example Conversation Flow

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

### Testing Scenarios

**Test 1: Validation**
- Invalid input: `"Hello"` → Bot rejects and asks for revision
- Valid input: `"What is 2+2?"` → Bot validates and proceeds

**Test 2: Refinement**
- Input with typos: `"what is derivitive of x squared"`
- Expected output: `"What is the derivative of x²?"`

**Test 3: Similarity**
- After accepting refinement, similarity check runs automatically
- Shows questions with >80% similarity if found

## API Documentation

### `POST /api/validate`

Validates if input is a valid mathematical question.

**Request:**
```json
{
  "message": "What is the derivative of x^2?"
}
```

**Response:**
```json
{
  "is_valid": true,
  "message": "✓ Your question is valid! Let's proceed to refinement.",
  "reasoning": "This is a clear mathematical question..."
}
```

### `POST /api/refine`

Refines a mathematical question for grammar, clarity, and formatting.

**Request:**
```json
{
  "message": "what is derivitive of x squared"
}
```

**Response:**
```json
{
  "refined_question": "What is the derivative of x²?",
  "changes_made": "Fixed spelling, improved formatting, added proper notation",
  "reasoning": "Improved clarity and mathematical notation..."
}
```

### `POST /api/similarity`

Finds semantically similar questions.

**Request:**
```json
{
  "message": "What is the derivative of x^2?"
}
```

**Response:**
```json
{
  "similar_questions": [
    {
      "question_id": 1,
      "question": "...",
      "similarity_score": 0.85,
      "domain": "Calculus",
      "subdomain": "Derivatives"
    }
  ],
  "threshold": 0.8
}
```

## Architecture & Design

### System Flow

```
User Input → Validation Service → Refinement Service → Similarity Service → Results
     ↑              ↓ (invalid)              ↓ (reject)
     └──────────────┴────────────────────────┘
```

### Backend Architecture

**Service-Oriented Design:**
- **API Layer** (`main.py`): Handles HTTP requests/responses
- **Service Layer** (`services/`): Business logic for each workflow
  - `validation_service.py`: Validates using LangChain + Groq
  - `refinement_service.py`: Refines questions
  - `similarity_service.py`: Finds similar questions using embeddings

### LangChain Integration

**Validation & Refinement:**
- Uses `ChatPromptTemplate` for structured prompts
- `PydanticOutputParser` for type-safe responses
- Chain composition: `Prompt → LLM → Parser`
- Async support for non-blocking operations

**Prompt Design:**
- Clear system messages with role definition
- Examples for few-shot learning
- Structured output with reasoning

### Similarity Implementation

**Embedding Model:** `all-MiniLM-L6-v2`
- 384-dimensional embeddings
- Fast inference (~80MB model)
- Good performance on mathematical text

**FAISS Index:**
- Pre-computed index for fast search
- Cosine similarity via L2 normalization
- Configurable threshold (default 80%)

### Error Handling

**Multi-layer Approach:**
1. **Service Level**: Try-catch with fallbacks
2. **API Level**: HTTP exceptions with clear messages
3. **Frontend Level**: User-friendly error display

**Graceful Degradation:**
- If LLM fails → Basic validation fallback
- If refinement fails → Return original question
- System always responds (never crashes)

## Troubleshooting

### "GROQ_API_KEY not set" Error

**Solution:**
- Make sure you set the environment variable in the same terminal where you run the server
- Restart the terminal after setting the variable
- Verify: `echo $GROQ_API_KEY` (Linux/Mac) or `echo %GROQ_API_KEY%` (Windows)

### "ModuleNotFoundError" Errors

**Solution:**
```bash
pip install -r requirements.txt
```

If still failing:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### "Questions file not found" Warning

**Solution:**
- Ensure `question.json` is in the project root directory
- The similarity check will still work, just with an empty database

### Port 8000 Already in Use

**Solution:**
- Change port in `run_server.py` or use:
  ```bash
  uvicorn backend.main:app --port 8001
  ```
- Update `API_BASE_URL` in `frontend/app.js` if using different port

### Frontend Can't Connect to Backend

**Solution:**
- Check that backend is running on `http://localhost:8000`
- Check browser console (F12) for CORS errors
- Verify `API_BASE_URL` in `frontend/app.js` matches your backend URL
- Make sure CORS is enabled (it is by default)

### Import Errors with LangChain

**Solution:**
```bash
pip install --upgrade langchain langchain-core langchain-groq
```

Check Python version (3.8+ required):
```bash
python --version
```

### First Similarity Check is Slow

**This is normal!** The embedding model (~80MB) loads on first use. Subsequent checks are fast.

## Configuration

### Environment Variables

- `GROQ_API_KEY` - Required. Your Groq API key

### Configurable Settings

**Similarity Threshold:**
- Default: 0.8 (80%)
- Location: `backend/services/similarity_service.py`
- Change in `find_similar()` method

**LLM Model:**
- Default: `llama-3.1-70b-versatile`
- Location: `backend/services/validation_service.py` and `refinement_service.py`
- Change in service `__init__` methods

**Server Port:**
- Default: 8000
- Location: `run_server.py`
- Change the `port` parameter

## Requirements Fulfillment

✅ **User Input Phase**: Chatbot prompts for question  
✅ **Validation Loop**: Validates and loops until valid  
✅ **Refinement Phase**: Refines with accept/reject option  
✅ **Similarity Check**: Semantic similarity >80% threshold  
✅ **User Interface**: Functional chat interface  
✅ **Backend**: Python + FastAPI + LangChain  
✅ **LLM**: Groq API (alternative to GPT-5)  
✅ **Similarity**: FAISS + SentenceTransformers  
✅ **Frontend**: HTML/JS chat interface  
✅ **Data Source**: question.json loaded correctly  

## Performance Notes

- **First similarity check**: May take 10-30 seconds (loading embedding model)
- **Subsequent checks**: Fast (< 1 second)
- **LLM responses**: Usually < 2 seconds (depends on Groq API)
- **FAISS index**: Built once on service initialization

## Next Steps

Once everything is working:

1. **Customize Prompts**: Edit prompts in `backend/services/validation_service.py` and `refinement_service.py`
2. **Adjust Similarity**: Change threshold in `backend/services/similarity_service.py`
3. **Modify UI**: Edit `frontend/styles.css` for styling
4. **Add Questions**: Add more questions to `question.json`

## Support

If you encounter issues:

1. Check server logs in the terminal
2. Check browser console (F12) for frontend errors
3. Verify all files are in correct locations
4. Ensure environment variables are set correctly
5. Run `python test_imports.py` to verify structure

## License

This project is provided as-is for the challenge evaluation.

---

**Status**: ✅ Complete and Ready for Testing

**Last Updated**: All requirements implemented with comprehensive error handling and documentation.
