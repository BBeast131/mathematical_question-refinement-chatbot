# Mathematical Question Refinement Chatbot

A chatbot application that helps users refine their mathematical questions through validation, refinement, and similarity checking using LangChain, Groq API, and semantic embeddings.

## Features

1. **User Input Phase**: Chatbot prompts for a mathematical question
2. **Validation Loop**: Validates if input is a valid mathematical question using LangChain + Groq
3. **Refinement Phase**: Refines questions for grammar, clarity, and formatting
4. **Similarity Check**: Finds semantically similar questions using embeddings (FAISS + SentenceTransformers)
5. **Interactive UI**: Clean chat interface for the conversation flow

## Architecture

```
backend/
├── main.py                 # FastAPI application
└── services/
    ├── validation_service.py    # Validates mathematical questions
    ├── refinement_service.py    # Refines questions
    └── similarity_service.py    # Finds similar questions using embeddings

frontend/
├── index.html             # Chat interface
├── styles.css             # Styling
└── app.js                 # Frontend logic

question.json              # Sample mathematical questions database
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js (optional, for serving frontend)
- Groq API key ([Get one here](https://console.groq.com/))

### Installation

1. **Clone or navigate to the project directory**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variable**:
   ```bash
   # Windows (PowerShell)
   $env:GROQ_API_KEY="your-groq-api-key-here"
   
   # Windows (CMD)
   set GROQ_API_KEY=your-groq-api-key-here
   
   # Linux/Mac
   export GROQ_API_KEY="your-groq-api-key-here"
   ```

4. **Ensure `question.json` is in the project root** (it should already be there)

### Running the Application

1. **Start the backend server**:
   ```bash
   cd backend
   python main.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`

2. **Open the frontend**:
   - Simply open `frontend/index.html` in a web browser, OR
   - Use a simple HTTP server:
     ```bash
     # Python
     cd frontend
     python -m http.server 3000
     
     # Node.js
     npx http-server frontend -p 3000
     ```
   - Navigate to `http://localhost:3000` in your browser

3. **Start chatting!** Enter a mathematical question and follow the flow.

## API Endpoints

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
  "reasoning": "..."
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
  "reasoning": "..."
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

## Design Decisions

### Backend Architecture
- **FastAPI**: Modern, fast Python web framework with automatic API documentation
- **LangChain**: Provides structured workflows for LLM interactions
- **Groq API**: Fast inference with LLaMA models (alternative to GPT-5)
- **Service Layer**: Separated concerns (validation, refinement, similarity)

### Similarity Check
- **SentenceTransformers**: Uses `all-MiniLM-L6-v2` for generating embeddings
- **FAISS**: Efficient similarity search with cosine similarity
- **Threshold**: 80% similarity threshold as specified

### Frontend
- **Vanilla JavaScript**: Simple, no framework dependencies
- **State Management**: Client-side state machine for conversation flow
- **UX**: Clear visual feedback, action buttons, status indicators

### Prompt Design
- **Validation Prompt**: Clear criteria for valid mathematical questions
- **Refinement Prompt**: Focuses on grammar, clarity, formatting while preserving meaning
- **Structured Output**: Uses Pydantic models for consistent LLM responses

## Error Handling

- Graceful fallbacks if LLM calls fail
- Clear error messages to users
- Logging for debugging
- Input validation and sanitization

## Testing the Application

1. **Test validation**:
   - Try: "What is 2+2?" (should be valid)
   - Try: "Hello" (should be invalid)

2. **Test refinement**:
   - Enter a question with typos or poor formatting
   - Review the refined version

3. **Test similarity**:
   - Enter a question similar to one in `question.json`
   - Check if similar questions are detected

## Troubleshooting

- **"GROQ_API_KEY not set"**: Make sure you've set the environment variable
- **"Questions file not found"**: Ensure `question.json` is in the project root
- **CORS errors**: The backend includes CORS middleware, but check if the frontend URL matches
- **Port conflicts**: Change the port in `main.py` or use `--port` with uvicorn

## Future Enhancements

- Session management for multi-user support
- Database storage for questions and conversations
- More sophisticated similarity algorithms
- Support for LaTeX rendering
- Export refined questions

## License

This project is provided as-is for the challenge evaluation.

