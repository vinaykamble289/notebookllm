#!/usr/bin/env python3
"""
Setup script for the Academic Reasoning Engine with OpenRouter AI DeepSeek
This script helps configure and test the reasoning engine setup.
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'httpx',
        'openai',
        'requests',
        'langchain',
        'faiss-cpu',
        'sentence-transformers'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(missing_packages):
    """Install missing dependencies"""
    if not missing_packages:
        return True
    
    print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install'
        ] + missing_packages)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment variables"""
    env_file = Path("backend/.env")
    
    # Get OpenRouter API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("\n🔑 OpenRouter API Key Setup")
        print("You need an OpenRouter API key to use the DeepSeek reasoning engine.")
        print("Get your API key from: https://openrouter.ai/keys")
        
        api_key = input("Enter your OpenRouter API key (or press Enter to skip): ").strip()
        
        if api_key:
            # Set environment variable for current session
            os.environ["OPENROUTER_API_KEY"] = api_key
            print("✅ API key set for current session")
        else:
            print("⚠️ No API key provided. You'll need to set OPENROUTER_API_KEY later.")
    else:
        print(f"✅ OpenRouter API key found: {api_key[:8]}...")
    
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_content = f"""
# OpenRouter AI Configuration
OPENROUTER_API_KEY={api_key or 'your_openrouter_api_key_here'}
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_APP_NAME=RAG-Academic-Assistant

# Academic Reasoning Engine Configuration
REASONING_MODEL=deepseek/deepseek-chat
REASONING_MAX_TOKENS=2048
REASONING_TEMPERATURE=0.7
ENABLE_REASONING=true

# Existing configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=google/flan-t5-base
MAX_TOKENS=512
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
"""
        with open(env_file, 'w') as f:
            f.write(env_content.strip())
        print("✅ Environment file created")
    else:
        print("✅ Environment file already exists")
        
        # Check if OpenRouter config exists in .env
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        if 'OPENROUTER_API_KEY' not in env_content and api_key:
            print("📝 Adding OpenRouter configuration to existing .env file...")
            with open(env_file, 'a') as f:
                f.write(f"\n\n# OpenRouter AI Configuration\nOPENROUTER_API_KEY={api_key}\n")
            print("✅ OpenRouter configuration added")

async def test_reasoning_engine():
    """Test the reasoning engine"""
    print("\n🧪 Testing Academic Reasoning Engine with OpenRouter AI DeepSeek...")
    
    try:
        # Add backend to path
        sys.path.append(str(Path("backend").absolute()))
        
        from app.core.reasoning_engine import reasoning_engine
        from langchain.schema import Document
        
        # Initialize
        await reasoning_engine.initialize()
        print("✅ Reasoning engine initialized")
        
        # Test with sample document
        test_doc = Document(
            page_content="This study examines machine learning applications in natural language processing. The research methodology involved training transformer models on academic datasets with statistical validation using t-tests.",
            metadata={"source": "test_paper.pdf", "document_id": "test1"}
        )
        
        # Test reasoning
        result = await reasoning_engine.reason(
            "What are the main findings about machine learning?",
            [test_doc]
        )
        
        print(f"✅ Reasoning test successful:")
        print(f"   - Type: {result['reasoning_type']}")
        print(f"   - Confidence: {result['confidence']:.2f}")
        print(f"   - Quality: {result['academic_quality']}")
        print(f"   - Model: {result.get('model_used', 'N/A')}")
        print(f"   - Tokens: {result.get('tokens_used', 'N/A')}")
        print(f"   - Preview: {result['reasoning'][:150]}...")
        
        # Cleanup
        await reasoning_engine.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Reasoning engine test failed: {e}")
        if "API key" in str(e):
            print("💡 Make sure you have set a valid OpenRouter API key")
        return False

def main():
    """Main setup function"""
    print("🚀 Academic Reasoning Engine Setup (OpenRouter AI DeepSeek)")
    print("=" * 65)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check dependencies
    missing = check_dependencies()
    
    # Install missing dependencies
    if missing:
        install_choice = input(f"\nInstall missing packages? (y/n): ").lower()
        if install_choice == 'y':
            if not install_dependencies(missing):
                return False
        else:
            print("❌ Cannot proceed without required dependencies")
            return False
    
    # Setup environment
    setup_environment()
    
    # Test reasoning engine
    test_choice = input(f"\nTest the reasoning engine? (y/n): ").lower()
    if test_choice == 'y':
        try:
            success = asyncio.run(test_reasoning_engine())
            if not success:
                return False
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Make sure your OpenRouter API key is set in backend/.env")
    print("2. Start the backend: cd backend && python main.py")
    print("3. Upload some academic documents")
    print("4. Try the academic reasoning features")
    print("5. Open frontend_reasoning_demo.html to test the interface")
    
    print("\n💡 OpenRouter AI DeepSeek Features:")
    print("   - Advanced reasoning capabilities")
    print("   - Better academic language understanding")
    print("   - Improved citation detection")
    print("   - More reliable API access")
    print("   - Usage tracking and analytics")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)