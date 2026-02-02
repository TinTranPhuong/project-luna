import os
import subprocess
import sys
from pathlib import Path

# Configuration for the project structure
PROJECT_STRUCTURE = {
    "extension": [
        "background", "content", "popup", "sidebar", "options", "shared", "assets"
    ],
    "server": [
        "api", "agents", "core", "tools", "rag", "governance", "handoff", "memory", "monitoring",
        "models", "data"
    ],
    "infrastructure": [
        "docker", "terraform", "k8s",
        "monitoring/prometheus", "monitoring/grafana", "monitoring/loki"
    ],
    "scripts": [],
    "tests": ["backend", "extension", "e2e"],
    "docs": []
}

SERVER_DEPENDENCIES = [
    "fastapi", "uvicorn[standard]", "pydantic", "python-dotenv",
    "langchain", "langchain-community", "chromadb", "sentence-transformers"
]

SERVER_DEV_DEPENDENCIES = ["pytest"]

EXTENSION_DEV_DEPS = [
    "typescript", "webpack", "webpack-cli", "ts-loader",
    "eslint", "prettier", "eslint-config-prettier",
    "@types/chrome", "@types/react", "@types/react-dom"
]

EXTENSION_DEPS = ["react", "react-dom", "lucide-react"]

def run_command(command, cwd=None, shell=False):
    """Executes a shell command and handles errors."""
    try:
        # On Windows, shell=True is often required for npm/poetry commands to be found
        is_windows = sys.platform.startswith('win')
        use_shell = shell or is_windows
        
        print(f"🔄 Running: {' '.join(command) if isinstance(command, list) else command}...")
        subprocess.run(
            command, 
            cwd=cwd, 
            check=True, 
            shell=use_shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("✅ Success")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing command: {e}")
        print(f"   Stderr: {e.stderr}")
        # We don't exit here to allow the script to attempt remaining steps
        # but in a strict CI environment you might want to sys.exit(1)

def step_0_1_init_git():
    print("\n--- 🛠️  Task 0.1: Initialize Git Repository ---")
    if os.path.exists(".git"):
        print("ℹ️  Git repository already initialized.")
    else:
        run_command(["git", "init"])
        
        # Create a basic README if it doesn't exist
        if not os.path.exists("README.md"):
            with open("README.md", "w") as f:
                f.write("# AI Browser Assistant\n\nLocal-first AI assistant for your browser.")
        
        run_command(["git", "add", "README.md"])
        run_command(["git", "commit", "-m", "Initial commit: Project kickoff"])

def step_0_2_folder_structure():
    print("\n--- 📂 Task 0.2: Setup Project Folder Structure ---")
    base_path = Path.cwd()

    for root_dir, sub_dirs in PROJECT_STRUCTURE.items():
        # Create root directory
        root_path = base_path / root_dir
        root_path.mkdir(exist_ok=True)
        print(f"Created: {root_dir}/")

        # Create subdirectories
        for sub in sub_dirs:
            sub_path = root_path / sub
            sub_path.mkdir(parents=True, exist_ok=True)
            # Create .gitkeep for empty leaf directories to ensure they are tracked
            gitkeep = sub_path / ".gitkeep"
            gitkeep.touch()
    
    # Specific .gitkeep for data/models folders if not covered
    (base_path / "server" / "models" / ".gitkeep").touch()
    (base_path / "server" / "data" / ".gitkeep").touch()

def step_0_3_0_4_setup_python():
    print("\n--- 🐍 Task 0.3 & 0.4: Setup Python Backend (Server) ---")
    server_path = Path.cwd() / "server"
    
    # Check if poetry is installed
    try:
        subprocess.run(["poetry", "--version"], check=True, stdout=subprocess.DEVNULL, shell=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Poetry not found. Please install Poetry first (pip install poetry).")
        return

    # Initialize Poetry if pyproject.toml doesn't exist
    if not (server_path / "pyproject.toml").exists():
        run_command(
            ["poetry", "init", "--name", "ai-browser-server", 
             "--description", "Local AI Server backend", 
             "--author", "DevUser", "-n"],
            cwd=server_path
        )
    
    # Add Dependencies
    print("📦 Installing Python dependencies (this may take a minute)...")
    run_command(["poetry", "add"] + SERVER_DEPENDENCIES, cwd=server_path)
    run_command(["poetry", "add", "--group", "dev"] + SERVER_DEV_DEPENDENCIES, cwd=server_path)
    
    # Install env
    run_command(["poetry", "install"], cwd=server_path)

def step_0_5_setup_node():
    print("\n--- ⚛️  Task 0.5: Setup Node.js Extension ---")
    ext_path = Path.cwd() / "extension"

    # Check for npm
    try:
        subprocess.run(["npm", "--version"], check=True, stdout=subprocess.DEVNULL, shell=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm not found. Please install Node.js.")
        return

    # Initialize npm
    if not (ext_path / "package.json").exists():
        run_command(["npm", "init", "-y"], cwd=ext_path)

    # Install Dev Dependencies
    print("📦 Installing Node dev dependencies...")
    run_command(["npm", "install", "--save-dev"] + EXTENSION_DEV_DEPS, cwd=ext_path)

    # Install Runtime Dependencies
    print("📦 Installing Node runtime dependencies...")
    run_command(["npm", "install"] + EXTENSION_DEPS, cwd=ext_path)

    # Initialize TypeScript config
    if not (ext_path / "tsconfig.json").exists():
        run_command(["npx", "tsc", "--init"], cwd=ext_path)

def main():
    print("🚀 Starting AI Browser Assistant Project Setup...")
    
    step_0_1_init_git()
    step_0_2_folder_structure()
    step_0_3_0_4_setup_python()
    step_0_5_setup_node()
    
    print("\n✅ Setup Complete!")
    print("\nNext Steps:")
    print("1. cd server && poetry shell  -> To work on backend")
    print("2. cd extension && npm run build -> To build extension (once webpack is configured)")

if __name__ == "__main__":
    main()