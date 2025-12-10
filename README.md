# Mathematical Question Refinement Chatbot

A chatbot application that helps users refine their mathematical questions through validation, refinement, and similarity checking.

## How to Run

### Step 1: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

**Note:** Use `python -m pip` instead of just `pip` to avoid path issues.

### Step 2: Set Up API Key

Create a `.env` file in the project root (same folder as `requirements.txt`) with your Groq API key:

```
GROQ_API_KEY=your-api-key-here
```

Get your free API key from: https://console.groq.com/

### Step 3: Start Backend Server

```bash
python run_server.py
```

The server will start on `http://localhost:8000`

### Step 4: Start Frontend Server

Open a new terminal and run:

```bash
cd frontend
python -m http.server 3000
```

### Step 5: Open in Browser

Open your browser and go to: **http://localhost:3000**

### Step 6: Test It

Enter a mathematical question like:
- "What is the derivative of x squared?"
- "Prove that square root of 2 is irrational"

The chatbot will:
1. Validate your question
2. Refine it for clarity
3. Check for similar questions

## Project Structure

```
mathematical_question-refinement-chatbot/
├── .env                    # Your API key (create this file)
├── backend/
│   ├── main.py
│   └── services/
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── question.json
├── requirements.txt
└── run_server.py
```

## Troubleshooting

**"Failed to fetch" error:**
- Make sure backend server is running (Step 3)
- Make sure frontend server is running (Step 4)
- Check that both are on ports 8000 and 3000

**"GROQ_API_KEY not set" error:**
- Make sure `.env` file is in project root (not in backend folder)
- Format: `GROQ_API_KEY=your-key-here` (no quotes)

**Port already in use:**
- Close other applications using ports 8000 or 3000
- Or change ports in `run_server.py` and `frontend/app.js`
