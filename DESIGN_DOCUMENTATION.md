# Design Documentation

## Overview

This document provides a comprehensive explanation of the design decisions, architecture, and implementation details for the Mathematical Question Refinement Chatbot.

## System Architecture

### High-Level Flow

```
User Input → Validation Service → Refinement Service → Similarity Service → Results
     ↑              ↓ (invalid)              ↓ (reject)
     └──────────────┴────────────────────────┘
```

### Component Responsibilities

#### 1. Validation Service (`backend/services/validation_service.py`)

**Purpose**: Determine if user input is a valid mathematical question.

**Implementation**:
- Uses LangChain with Groq's LLaMA 3.1 70B model
- Structured output via Pydantic (`ValidationResult`)
- Temperature: 0.1 (low for consistent validation)
- Fallback: Basic length check if LLM fails

**Prompt Strategy**:
- Role: Expert mathematician/educator
- Criteria: 4-point checklist for validity
- Examples: Few-shot learning with valid/invalid examples
- Output: Boolean + reasoning + suggestions

#### 2. Refinement Service (`backend/services/refinement_service.py`)

**Purpose**: Improve grammar, clarity, and formatting while preserving mathematical meaning.

**Implementation**:
- Same LLM setup as validation
- Temperature: 0.3 (slightly higher for creative improvements)
- Structured output: `RefinementResult` with changes tracking

**Prompt Strategy**:
- Role: Expert mathematical editor
- Guidelines: 6 do's and 4 don'ts
- Constraint: Preserve mathematical content
- Output: Refined question + change description + reasoning

#### 3. Similarity Service (`backend/services/similarity_service.py`)

**Purpose**: Find semantically similar questions using embeddings.

**Implementation**:
- Embedding model: `all-MiniLM-L6-v2` (384 dimensions)
- Index: FAISS IndexFlatIP (cosine similarity)
- Threshold: 0.8 (80% similarity)
- Pre-computed index for fast search

**Process**:
1. Load questions from JSON
2. Generate embeddings for all questions
3. Build FAISS index (normalized for cosine similarity)
4. For each query: embed → search → filter by threshold → rank

#### 4. API Layer (`backend/main.py`)

**Endpoints**:
- `POST /api/validate`: Validation workflow
- `POST /api/refine`: Refinement workflow
- `POST /api/similarity`: Similarity check
- `POST /api/chat`: Unified chat endpoint (for future expansion)

**Features**:
- CORS enabled for frontend
- Lazy service initialization
- Error handling with HTTP exceptions
- Structured responses (Pydantic models)

#### 5. Frontend (`frontend/`)

**State Machine**:
```
initial → validating → valid → refining → refined → checking_similarity → complete
   ↑         ↓ (invalid)
   └─────────┘
```

**Features**:
- Real-time chat interface
- Action buttons (Accept/Reject)
- Status indicators
- Conversation history
- Error handling

## LangChain Integration Details

### Chain Composition

Both validation and refinement use the same pattern:

```python
prompt = ChatPromptTemplate.from_messages([...])
chain = prompt | llm | output_parser
result = await chain.ainvoke({"input": user_input})
```

**Why this works**:
- `|` operator creates a pipeline
- Each component handles one concern
- Async support for non-blocking operations
- Type safety via Pydantic output parser

### Structured Outputs

Using `PydanticOutputParser` ensures:
- Consistent JSON responses
- Type validation
- Clear error messages if parsing fails
- Self-documenting API responses

### Prompt Engineering

**Validation Prompt**:
- System message sets context and role
- Human message provides the input
- Format instructions guide JSON output
- Examples enable few-shot learning

**Refinement Prompt**:
- Similar structure
- More detailed guidelines
- Emphasis on preservation constraints
- Change tracking in output

## Semantic Similarity Implementation

### Why Embeddings?

- **Semantic understanding**: Captures meaning, not just keywords
- **Context awareness**: Understands mathematical concepts
- **Scalability**: Fast search even with large databases

### Model Choice: `all-MiniLM-L6-v2`

**Pros**:
- Fast inference (~80MB model)
- Good performance on diverse text
- 384 dimensions (balance of quality and speed)
- Pre-trained on large corpus

**Cons**:
- May not capture all mathematical nuances
- Fixed vocabulary (handles most math notation)

### FAISS Index

**Type**: `IndexFlatIP` (Inner Product)

**Why**:
- Simple and fast for small-medium datasets
- Exact search (no approximation)
- Cosine similarity via L2 normalization + inner product

**Process**:
1. Normalize all embeddings (L2 norm = 1)
2. Inner product = cosine similarity
3. Search returns top-k results
4. Filter by threshold (0.8)

## Error Handling Strategy

### Three-Layer Approach

1. **Service Layer**:
   - Try-catch around LLM calls
   - Fallback logic (basic validation)
   - Logging for debugging

2. **API Layer**:
   - HTTP exception handling
   - User-friendly error messages
   - Status codes (400, 500, etc.)

3. **Frontend Layer**:
   - Display error messages
   - Retry mechanisms
   - Status indicators

### Graceful Degradation

- If validation fails → Basic length check
- If refinement fails → Return original question
- If similarity fails → Return empty list
- System always responds (never crashes)

## Testing Strategy

### Manual Testing Scenarios

1. **Validation**:
   - Valid: "What is the derivative of x^2?"
   - Invalid: "Hello"
   - Edge case: "2+2" (too short, no context)

2. **Refinement**:
   - Typo: "derivitive" → "derivative"
   - Formatting: "x squared" → "x²"
   - Grammar: "what is" → "What is"

3. **Similarity**:
   - Similar question in database
   - Unique question (no matches)
   - Threshold boundary (79% vs 81%)

## Performance Considerations

### Backend
- Lazy service initialization (faster startup)
- Async operations (non-blocking)
- Pre-computed FAISS index (fast similarity)

### Frontend
- Client-side state management (no server round-trips)
- Efficient DOM updates
- Minimal dependencies (fast load)

## Security Considerations

1. **API Key**: Environment variable (not in code)
2. **Input Sanitization**: Pydantic validation
3. **CORS**: Configured for development (restrict in production)
4. **XSS Prevention**: HTML escaping in frontend

## Future Enhancements

1. **Session Management**: Track multiple users
2. **Database**: Store questions and conversations
3. **Caching**: Cache embeddings and LLM responses
4. **Rate Limiting**: Prevent API abuse
5. **LaTeX Rendering**: Better math notation display
6. **Multi-language**: Support for other languages

## Conclusion

This implementation provides:
- ✅ Clear architecture with separation of concerns
- ✅ Proper LangChain integration with structured outputs
- ✅ Effective prompt design for validation and refinement
- ✅ Robust error handling with graceful degradation
- ✅ Efficient semantic similarity using embeddings
- ✅ Simple, functional UI for chat experience
- ✅ Comprehensive documentation and explainability

The system is production-ready with room for enhancements based on user feedback and requirements.

