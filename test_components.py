#!/usr/bin/env python3
"""Test script to verify core components work without GUI."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_components():
    """Test core components."""
    
    print("Testing core components...")
    print("-" * 50)
    
    # Test configuration
    print("\n1. Testing Configuration Manager...")
    try:
        from services.configuration_manager import ConfigurationManager
        config_manager = ConfigurationManager()
        config = config_manager.load()
        print(f"   ✓ Config loaded successfully")
        print(f"   - Output folder: {config.output_folder}")
        print(f"   - Log directory: {config.log_directory}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test models
    print("\n2. Testing Models...")
    try:
        from models.document import Document
        from models.keyword import Keyword
        from models.keyword_history import KeywordHistory
        
        doc = Document.from_path(__file__)
        print(f"   ✓ Document model works: {doc.filename}")
        
        kw = Keyword.from_text("TEST")
        print(f"   ✓ Keyword model works: {kw.text}")
        
        history = KeywordHistory()
        history.add("TEST")
        print(f"   ✓ KeywordHistory works: {len(history)} keywords")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test parsers
    print("\n3. Testing Parsers...")
    try:
        from parsers.factory import ParserFactory
        print(f"   ✓ Parser factory available")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test extractors
    print("\n4. Testing Extractors...")
    try:
        from extractors.extraction_engine import ExtractionEngine
        print(f"   ✓ Extraction engine available")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test controllers
    print("\n5. Testing Controllers...")
    try:
        from controllers.state_manager import StateManager
        from controllers.thread_coordinator import ThreadCoordinator
        
        state_mgr = StateManager()
        print(f"   ✓ StateManager works")
        
        thread_coord = ThreadCoordinator()
        print(f"   ✓ ThreadCoordinator works")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    print("\n" + "-" * 50)
    print("✅ All core components working!")
    print("\nNote: GUI requires tkinter. Install Python 3.10+ with tkinter support:")
    print("  brew install python@3.11")
    print("  python3.11 src/main.py")
    
    return True

if __name__ == '__main__':
    success = test_components()
    sys.exit(0 if success else 1)
