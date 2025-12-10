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
   # Recommended: Use the run script
   python run_server.py
   
   # Or using uvicorn directly:
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

## Design Decisions & Explainability

### Architecture and Design Clarity

The application follows a **service-oriented architecture** with clear separation of concerns:

1. **API Layer** (`backend/main.py`): Handles HTTP requests/responses, routing, and error handling
2. **Service Layer** (`backend/services/`): Contains business logic for each workflow step
   - `validation_service.py`: Validates mathematical questions
   - `refinement_service.py`: Refines questions for quality
   - `similarity_service.py`: Finds similar questions using embeddings
3. **Frontend Layer** (`frontend/`): Manages user interaction and conversation state

This separation allows:
- Easy testing of individual components
- Clear responsibility boundaries
- Simple extension with new features
- Independent scaling of services

### LangChain Integration

**Validation Workflow:**
- Uses `ChatPromptTemplate` for structured prompt management
- Implements `PydanticOutputParser` for type-safe LLM responses
- Creates a chain: `Prompt → LLM → Parser` using LangChain's pipe operator (`|`)
- Async support with `ainvoke()` for non-blocking operations

**Refinement Workflow:**
- Similar chain structure but with different prompt and output schema
- Temperature set to 0.3 (vs 0.1 for validation) to allow creative improvements
- Preserves mathematical meaning while improving presentation

**Why LangChain?**
- Standardized interface for LLM interactions
- Built-in support for structured outputs (Pydantic)
- Easy to swap LLM providers (Groq, OpenAI, etc.)
- Chain composition enables complex workflows

### Prompt Design

**Validation Prompt Strategy:**
- **System message** defines the role (expert mathematician/educator)
- **Clear criteria** for valid mathematical questions (4 key points)
- **Examples** of valid and invalid inputs for few-shot learning
- **Structured output** ensures consistent JSON responses

**Refinement Prompt Strategy:**
- **Editor role** emphasizes grammar, clarity, formatting
- **Explicit guidelines** (6 do's and 4 don'ts) to prevent over-editing
- **Preservation constraint** ensures mathematical content isn't altered
- **Change tracking** in output helps users understand improvements

**Design Rationale:**
- Prompts are self-contained and don't rely on conversation history
- Clear boundaries prevent prompt injection
- Structured outputs reduce parsing errors
- Examples guide the model's behavior

### Error Handling Strategy

**Multi-layer Error Handling:**

1. **Service Level:**
   - Try-catch blocks around LLM calls
   - Fallback validation (length check) if LLM fails
   - Graceful degradation (return original question if refinement fails)

2. **API Level:**
   - HTTP exception handling with meaningful error messages
   - Logging for debugging without exposing internals
   - Input validation via Pydantic models

3. **Frontend Level:**
   - User-friendly error messages
   - Status indicators (loading, error, success)
   - Retry mechanisms for failed requests

**Why This Approach:**
- Users always get a response (even if degraded)
- Errors are logged for debugging
- System remains functional even if one component fails

### Semantic Similarity Logic

**Embedding Model Choice:**
- **`all-MiniLM-L6-v2`**: 384-dimensional embeddings, fast inference
- Pre-trained on diverse text, good for mathematical content
- Small model size (~80MB) for quick loading

**FAISS Index:**
- **IndexFlatIP**: Inner product for cosine similarity (after L2 normalization)
- Pre-computed index for fast similarity search
- Handles 10+ questions efficiently (scales to thousands)

**Similarity Calculation:**
1. Normalize embeddings (L2 normalization)
2. Use inner product (equivalent to cosine similarity for normalized vectors)
3. Filter by threshold (0.8 = 80% similarity)
4. Sort by similarity score (descending)

**Why This Approach:**
- Semantic understanding (not just keyword matching)
- Fast search even with large question databases
- Configurable threshold for different use cases
- Returns ranked results for user review

### UI Simplicity and Usability

**Design Principles:**
- **Minimal but functional**: Focus on conversation flow, not flashy UI
- **Clear visual hierarchy**: Bot vs user messages, status indicators
- **Action buttons**: Quick accept/reject for refinement
- **Real-time feedback**: Status bar shows current operation
- **Conversation history**: Scrollable chat for context

**State Management:**
- Client-side state machine tracks conversation phase
- Prevents invalid state transitions
- Handles user responses appropriately based on phase

**User Experience Flow:**
1. User enters question → Validation
2. If invalid → Request revision (loop)
3. If valid → Show refinement
4. User accepts/rejects → Similarity check or new refinement
5. Show similar questions → Complete

### Completeness Checklist

✅ **User Input Phase**: Chatbot prompts for question  
✅ **Validation Loop**: Backend validates, loops until valid  
✅ **Refinement Phase**: Refines question, allows accept/reject  
✅ **Similarity Check**: Semantic similarity with >80% threshold  
✅ **UI**: Chat interface with conversation history  
✅ **LangChain Integration**: Proper chains for validation and refinement  
✅ **Error Handling**: Graceful degradation and user-friendly messages  
✅ **Documentation**: README with setup and design explanations

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

