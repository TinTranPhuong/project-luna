import os
import subprocess
import sys
import importlib
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}\n {title}\n{'='*60}")

def check_command(command, cwd=None, shell=False):
    try:
        # Windows needs shell=True for some commands like npm
        use_shell = shell or (sys.platform == 'win32')
        result = subprocess.run(
            command, 
            cwd=cwd, 
            shell=use_shell, 
            capture_output=True, 
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_server():
    print_header("🧠 Checking Server (Python/Poetry)")
    server_path = Path("server")
    
    # Check 1: Poetry Environment
    passed, out, err = check_command(["poetry", "env", "info"], cwd=server_path, shell=True)
    if not passed:
        print("❌ Poetry environment not found.")
        return False

    # Check 2: Import Libraries
    # We run a mini-script inside the poetry environment to verify imports
    check_script = """
import importlib, sys
deps = ['fastapi', 'uvicorn', 'langchain', 'chromadb', 'sentence_transformers']
missing = []
for dep in deps:
    try:
        importlib.import_module(dep)
        print(f'✅ {dep} is installed')
    except ImportError:
        missing.append(dep)
        print(f'❌ {dep} is MISSING')
if missing: sys.exit(1)
"""
    passed, out, err = check_command(["poetry", "run", "python", "-c", check_script], cwd=server_path, shell=True)
    print(out)
    if not passed:
        print("⚠️  Server dependencies issue detected.")
        return False
    return True

def check_extension():
    print_header("🔌 Checking Extension (Node.js)")
    ext_path = Path("extension")
    
    # Check 1: node_modules exists
    if not (ext_path / "node_modules").exists():
        print("❌ node_modules folder missing. Run 'npm install' in extension folder.")
        return False

    # Check 2: React is installed
    passed, out, err = check_command(["npm", "list", "react"], cwd=ext_path, shell=True)
    if passed:
        print("✅ React is installed")
        print("✅ Node environment looks healthy")
        return True
    else:
        print("❌ React not found in extension.")
        return False

def check_git_config():
    print_header("🛡️ Checking Git Configuration")
    
    # 1. Check for .gitignore (The #1 cause of 'Green Folders')
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("❌ MISSING: .gitignore file")
        print("   (This is why your folders are green! Git is trying to track temp files)")
        create = input("   👉 Create a standard .gitignore now? (y/n): ")
        if create.lower() == 'y':
            create_gitignore()
            print("✅ Created .gitignore")
        else:
            return False
    else:
        print("✅ .gitignore exists")

    # 2. Check Status
    passed, out, err = check_command(["git", "status"])
    print("\n--- Current Git Status ---")
    
    # Logic to detect if node_modules is accidentally tracked
    if "node_modules/" in out:
        print("⚠️  WARNING: Git is trying to track 'node_modules'!")
        print("   You should NOT commit this. The .gitignore fix will handle it.")
    elif "working tree clean" in out:
        print("✅ Git status: Clean (No green folders!)")
    else:
        print("ℹ️  Git status: Uncommitted changes present (Folders will be green)")
        print(out[:500] + "..." if len(out) > 500 else out)
    
    return True

def create_gitignore():
    content = """
# Python
__pycache__/
*.py[cod]
.env
.venv
env/
venv/
poetry.lock

# Node.js
node_modules/
dist/
build/
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
    with open(".gitignore", "w") as f:
        f.write(content.strip())

def main():
    print("🕵️ STARTING FINAL PROJECT AUDIT...")
    
    s_ok = check_server()
    e_ok = check_extension()
    g_ok = check_git_config()
    
    print_header("🏁 Audit Summary")
    if s_ok and e_ok and g_ok:
        print("🟢 SYSTEM READY. You can proceed to Phase 1.")
        print("   If folders are still green, run: git add . && git commit -m 'Final cleanup'")
    else:
        print("🔴 ISSUES FOUND. Please fix the items marked with ❌ above.")

if __name__ == "__main__":
    main()