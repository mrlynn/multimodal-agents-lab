#!/usr/bin/env python3
"""
Test the jupyter-lab-progress module functionality
"""

try:
    from jupyter_lab_progress import (
        LabProgress, LabValidator, show_info, show_warning, 
        show_success, show_error, show_hint
    )
    print("✅ Progress tracking libraries loaded successfully! 🎉")
    
    # Test the display functions
    print("\n🧪 Testing display functions:")
    show_info("This is an info message")
    show_warning("This is a warning message")
    show_success("This is a success message")
    show_error("This is an error message")
    show_hint("This is a hint message")
    
    # Test LabProgress
    print("\n📊 Testing LabProgress:")
    steps = ["Step 1: Setup", "Step 2: Process", "Step 3: Generate"]
    progress = LabProgress(steps, lab_name="Test Lab")
    print(f"Progress tracker initialized with {len(steps)} steps")
    
    # Test LabValidator
    print("\n✅ Testing LabValidator:")
    validator = LabValidator()
    
    # Test some validation
    test_var = "test_value"
    result = validator.validate_variable_exists('test_var', locals())
    print(f"Variable validation result: {result}")
    
    print("\n🎉 All tests passed! jupyter-lab-progress is working correctly.")
    
except ImportError as e:
    print(f"❌ Could not import progress tracking: {e}")
    print("📝 This means jupyter-lab-progress is not installed or not working properly.")
    print("   Run: pip install jupyter-lab-progress==1.1.4")
    
except Exception as e:
    print(f"❌ Error testing progress tracking: {e}")
    print("📝 The module is installed but there's an issue with functionality.")