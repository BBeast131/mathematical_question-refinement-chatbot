"""
Test script to verify all imports and basic structure work correctly
"""
import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test backend imports
        sys.path.insert(0, 'backend')
        from services.validation_service import ValidationService
        from services.refinement_service import RefinementService
        from services.similarity_service import SimilarityService
        print("[OK] All service imports successful")
        
        # Test main app
        from main import app
        print("[OK] Main app import successful")
        
        return True
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("Note: Some dependencies may not be installed. Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'backend/main.py',
        'backend/services/validation_service.py',
        'backend/services/refinement_service.py',
        'backend/services/similarity_service.py',
        'backend/services/__init__.py',
        'frontend/index.html',
        'frontend/app.js',
        'frontend/styles.css',
        'question.json',
        'requirements.txt',
        'run_server.py'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"[OK] {file}")
        else:
            print(f"[MISSING] {file}")
            all_exist = False
    
    return all_exist

def test_json_structure():
    """Test that question.json has correct structure"""
    print("\nTesting question.json structure...")
    
    try:
        import json
        with open('question.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list) and len(data) > 0:
            if 'question' in data[0]:
                print(f"[OK] question.json is valid with {len(data)} questions")
                return True
            else:
                print("[ERROR] question.json missing 'question' field")
                return False
        else:
            print("[ERROR] question.json is not a valid list")
            return False
    except Exception as e:
        print(f"[ERROR] Error reading question.json: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Mathematical Question Refinement Chatbot - Test Suite")
    print("=" * 50)
    
    structure_ok = test_file_structure()
    json_ok = test_json_structure()
    imports_ok = test_imports()
    
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  File Structure: {'[PASS]' if structure_ok else '[FAIL]'}")
    print(f"  JSON Structure: {'[PASS]' if json_ok else '[FAIL]'}")
    print(f"  Imports: {'[PASS]' if imports_ok else '[FAIL - dependencies may need installation]'}")
    print("=" * 50)
    
    if structure_ok and json_ok:
        print("\n[SUCCESS] Basic structure is correct!")
        print("   Install dependencies: pip install -r requirements.txt")
        print("   Set GROQ_API_KEY environment variable")
        print("   Run: python run_server.py")
    else:
        print("\n[FAIL] Some issues found. Please fix them before running.")

