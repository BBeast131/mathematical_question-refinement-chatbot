"""
Script to run the FastAPI server
"""
import uvicorn
import os
import sys

if __name__ == "__main__":
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  WARNING: GROQ_API_KEY environment variable is not set!")
        print("Please set it before running the server:")
        print("  Windows (PowerShell): $env:GROQ_API_KEY='your-key-here'")
        print("  Windows (CMD): set GROQ_API_KEY=your-key-here")
        print("  Linux/Mac: export GROQ_API_KEY='your-key-here'")
        print("\nContinuing anyway... (will fail when services initialize)")
    
    # Run the server
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

