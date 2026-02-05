#!/usr/bin/env python3
"""
Example: Using Prompt Versioning (Post 3)

This script demonstrates:
1. Loading versioned prompts
2. Getting specific versions
3. Listing available versions
4. Rendering prompt templates
5. Verifying prompt integrity
6. Creating new prompt versions
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.prompts import get_prompt_manager


def main():
    """Demonstrate prompt versioning features."""
    
    print("=" * 60)
    print("Post 3: Prompt Versioning Example")
    print("=" * 60)
    print()
    
    # Get prompt manager instance
    manager = get_prompt_manager()
    
    # Example 1: Load latest version
    print("1. Loading latest prompt version:")
    print("-" * 60)
    prompt = manager.get_prompt("clinical_summarization")
    
    if prompt:
        print(f"✓ Loaded: {prompt.task} v{prompt.version}")
        print(f"  Description: {prompt.description}")
        print(f"  Status: {prompt.status}")
        print(f"  Created: {prompt.created_at}")
        print(f"  Hash: {prompt.prompt_hash[:16]}...")
        print()
    else:
        print("✗ No prompt found!")
        print("  Make sure prompts/ directory contains prompt files")
        return
    
    # Example 2: List all versions
    print("2. Listing all versions:")
    print("-" * 60)
    versions = manager.list_versions("clinical_summarization")
    print(f"Found {len(versions)} version(s):")
    for v in versions:
        print(f"  - v{v}")
    print()
    
    # Example 3: Load specific version
    print("3. Loading specific version:")
    print("-" * 60)
    if versions:
        specific_prompt = manager.get_prompt("clinical_summarization", version=versions[0])
        if specific_prompt:
            print(f"✓ Loaded specific version: v{specific_prompt.version}")
        print()
    
    # Example 4: Render prompt template
    print("4. Rendering prompt template:")
    print("-" * 60)
    sample_note = """Patient presents with acute onset headache.
Denies trauma. Vital signs: BP 120/80, HR 72, Temp 98.6F.
Neurological exam normal. Assessment: Tension headache.
Plan: Acetaminophen 500mg PO PRN."""
    
    try:
        rendered = manager.render_user_prompt(prompt, note_text=sample_note)
        print("✓ Template rendered successfully")
        print(f"  Preview: {rendered[:100]}...")
        print()
    except ValueError as e:
        print(f"✗ Template rendering failed: {e}")
        print()
    
    # Example 5: Verify integrity
    print("5. Verifying prompt integrity:")
    print("-" * 60)
    is_valid = manager.validate_prompt_integrity(prompt)
    if is_valid:
        print("✓ Prompt integrity verified (hash matches)")
    else:
        print("✗ Prompt integrity check failed (hash mismatch)")
    print()
    
    # Example 6: Show prompt details
    print("6. Prompt details:")
    print("-" * 60)
    print(f"System Prompt Preview:")
    print(f"  {prompt.system_prompt[:100]}...")
    print()
    print(f"User Prompt Template:")
    print(f"  {prompt.user_prompt_template[:100]}...")
    print()
    
    if prompt.validation:
        print("Validation Rules:")
        for key, value in prompt.validation.items():
            print(f"  {key}: {value}")
        print()
    
    if prompt.metadata:
        print("Metadata:")
        for key, value in prompt.metadata.items():
            print(f"  {key}: {value}")
        print()
    
    # Example 7: Demonstrate version comparison
    print("7. Version comparison use case:")
    print("-" * 60)
    print("You can now:")
    print("  • Deploy new prompt versions without code changes")
    print("  • A/B test different prompts in production")
    print("  • Roll back to previous version instantly")
    print("  • Track which prompt generated each output")
    print("  • Meet regulatory requirements for reproducibility")
    print()
    
    # Example 8: Show how to create new version
    print("8. Creating a new version:")
    print("-" * 60)
    print("To create a new prompt version:")
    print()
    print("1. Copy existing YAML file:")
    print("   cp prompts/clinical_summarization_v1.0.0.yaml \\")
    print("      prompts/clinical_summarization_v1.1.0.yaml")
    print()
    print("2. Update the YAML file:")
    print("   - Change version: '1.1.0'")
    print("   - Update description")
    print("   - Modify system_prompt or user_prompt_template")
    print("   - Update created_at and metadata")
    print()
    print("3. Reload prompts (no restart needed!):")
    print("   manager.reload_prompts()")
    print()
    print("4. New version is now available")
    print()
    
    # Summary
    print("=" * 60)
    print("Summary: Prompt Versioning Benefits")
    print("=" * 60)
    print()
    print("✓ Prompts are versioned like code")
    print("✓ Complete audit trail (version + hash)")
    print("✓ No deployment needed for prompt changes")
    print("✓ Instant rollback capability")
    print("✓ A/B testing infrastructure")
    print("✓ Regulatory compliance built-in")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)