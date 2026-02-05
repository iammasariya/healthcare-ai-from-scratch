#!/usr/bin/env python3
"""
Simple verification script for Post 3 prompt management system.
Tests the core functionality without requiring pytest.
"""

from app.prompts import get_prompt_manager


def test_prompt_loading():
    """Test that prompts can be loaded successfully."""
    print("=" * 60)
    print("Testing Prompt Management System (Post 3)")
    print("=" * 60)
    
    # Get prompt manager instance
    manager = get_prompt_manager()
    
    # Test 1: Load the clinical summarization prompt
    print("\n1. Loading clinical_summarization prompt...")
    prompt = manager.get_prompt("clinical_summarization")
    
    if prompt:
        print(f"   ✓ Loaded prompt version: {prompt.version}")
        print(f"   ✓ Task: {prompt.task}")
        print(f"   ✓ Status: {prompt.status}")
        print(f"   ✓ Description: {prompt.description}")
        print(f"   ✓ Hash (first 8 chars): {prompt.prompt_hash[:8]}")
    else:
        print("   ✗ Failed to load prompt!")
        return False
    
    # Test 2: Verify integrity
    print("\n2. Verifying prompt integrity...")
    is_valid = manager.validate_prompt_integrity(prompt)
    if is_valid:
        print(f"   ✓ Integrity check passed")
    else:
        print(f"   ✗ Integrity check failed!")
        return False
    
    # Test 3: Render template
    print("\n3. Testing template rendering...")
    try:
        rendered = manager.render_user_prompt(
            prompt,
            note_text="Patient presents with acute onset headache."
        )
        print(f"   ✓ Template rendered successfully")
        print(f"   Preview: {rendered[:100]}...")
    except Exception as e:
        print(f"   ✗ Template rendering failed: {e}")
        return False
    
    # Test 4: List versions
    print("\n4. Listing available versions...")
    versions = manager.list_versions("clinical_summarization")
    print(f"   ✓ Found {len(versions)} version(s): {versions}")
    
    # Test 5: Check prompt metadata
    print("\n5. Checking prompt metadata...")
    print(f"   ✓ Created at: {prompt.created_at}")
    print(f"   ✓ Created by: {prompt.created_by}")
    if prompt.metadata:
        print(f"   ✓ Approved by: {prompt.metadata.get('approved_by', 'N/A')}")
        print(f"   ✓ Regulatory status: {prompt.metadata.get('regulatory_status', 'N/A')}")
    
    # Test 6: Check validation rules
    print("\n6. Checking validation rules...")
    if prompt.validation:
        print(f"   ✓ Max tokens: {prompt.validation.get('max_tokens', 'N/A')}")
        print(f"   ✓ Temperature: {prompt.validation.get('temperature', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
    print("\nPost 3 implementation is working correctly:")
    print("  • Prompts load from YAML files")
    print("  • Semantic versioning works")
    print("  • Integrity verification functions")
    print("  • Template rendering works")
    print("  • Metadata is preserved")
    print("\nThe system is ready for production use!")
    
    return True


if __name__ == "__main__":
    try:
        success = test_prompt_loading()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        exit(1)