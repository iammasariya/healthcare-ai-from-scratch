"""
Tests for prompt management system.

Tests the versioning, loading, and integrity verification of prompts.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from app.prompts import PromptManager, PromptVersion


@pytest.fixture
def temp_prompts_dir():
    """Create a temporary directory for test prompts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_prompt_v1(temp_prompts_dir):
    """Create a sample prompt version 1.0.0."""
    prompt_data = {
        "version": "1.0.0",
        "created_at": "2026-02-04T10:00:00Z",
        "created_by": "test@example.com",
        "status": "active",
        "task": "test_task",
        "description": "Test prompt version 1.0.0",
        "system_prompt": "You are a test assistant.",
        "user_prompt_template": "Process this: {input_text}",
        "validation": {
            "max_tokens": 100,
            "temperature": 0.5
        },
        "metadata": {
            "approved_by": "manager@example.com",
            "testing_notes": "Initial test prompt"
        }
    }
    
    prompt_file = Path(temp_prompts_dir) / "test_task_v1.0.0.yaml"
    with open(prompt_file, 'w') as f:
        yaml.dump(prompt_data, f)
    
    return prompt_file


@pytest.fixture
def sample_prompt_v1_1(temp_prompts_dir):
    """Create a sample prompt version 1.1.0."""
    prompt_data = {
        "version": "1.1.0",
        "created_at": "2026-02-05T10:00:00Z",
        "created_by": "test@example.com",
        "status": "active",
        "task": "test_task",
        "description": "Test prompt version 1.1.0 with improvements",
        "system_prompt": "You are an improved test assistant.",
        "user_prompt_template": "Process this carefully: {input_text}",
        "validation": {
            "max_tokens": 100,
            "temperature": 0.5
        },
        "metadata": {
            "approved_by": "manager@example.com",
            "testing_notes": "Improved test prompt"
        }
    }
    
    prompt_file = Path(temp_prompts_dir) / "test_task_v1.1.0.yaml"
    with open(prompt_file, 'w') as f:
        yaml.dump(prompt_data, f)
    
    return prompt_file


@pytest.fixture
def deprecated_prompt(temp_prompts_dir):
    """Create a deprecated prompt."""
    prompt_data = {
        "version": "0.9.0",
        "created_at": "2026-02-01T10:00:00Z",
        "created_by": "test@example.com",
        "status": "deprecated",
        "task": "test_task",
        "description": "Old deprecated prompt",
        "system_prompt": "You are an old assistant.",
        "user_prompt_template": "Process: {input_text}",
        "validation": {},
        "metadata": {}
    }
    
    prompt_file = Path(temp_prompts_dir) / "test_task_v0.9.0.yaml"
    with open(prompt_file, 'w') as f:
        yaml.dump(prompt_data, f)
    
    return prompt_file


class TestPromptManager:
    """Test suite for PromptManager."""
    
    def test_load_single_prompt(self, temp_prompts_dir, sample_prompt_v1):
        """Test loading a single prompt."""
        manager = PromptManager(prompts_dir=temp_prompts_dir)
        
        prompt = manager.get_prompt("test_task")
        
        assert prompt is not None
        assert prompt.version == "1.0.0"
        assert prompt.task == "test_task"
        assert prompt.system_prompt == "You are a test assistant."
        assert "{input_text}" in prompt.user_prompt_template
    
    def test_get_latest_version(self, temp_prompts_dir, sample_prompt_v1, sample_prompt_v1_1):
        """Test that get_prompt returns the latest version."""
        manager = PromptManager(prompts_dir=temp_prompts_dir)
        
        prompt = manager.get_prompt("test_task")
        
        assert prompt.version == "1.1.0"  # Should get the latest
    
    def test_get_specific_version(self, temp_prompts_dir, sample_prompt_v1, sample_prompt_v1_1):
        """Test getting a specific prompt version."""
        manager = PromptManager(prompts_dir=temp_prompts_dir)
        
        prompt_v1 = manager.get_prompt("test_task", version="1.0.0")
        prompt_v1_1 = manager.get_prompt("test_task", version="1.1.0")
        
        assert prompt_v1.version == "1.0.0"
        assert prompt_v1_1.version == "1.1.0"
        assert prompt_v1.system_prompt != prompt_v1_1.system_prompt
    
    def test_list_versions(self, temp_prompts_dir, sample_prompt_v1, sample_prompt_v1_1):
        """Test listing all versions for a task."""
        manager = PromptManager(prompts_dir=temp_prompts_dir)
        
        versions = manager.list_versions("test_task")
        
        assert len(versions) == 2
        assert "1.0.0" in versions
        assert "1.1.0" in versions
        # Should be in descending order (newest first)
        assert versions[0] == "1.1.0"
        assert versions[1] == "1.0.0"
    
    def test_deprecated_prompts_not_loaded(self, temp_prompts_dir, deprecated_prompt, sample_prompt_v1):
        """Test that deprecated prompts are not loaded into cache."""
        manager = PromptManager(prompts_dir=temp_prompts_dir)
        
        versions = manager.list_versions("test_task")
        
        # Only active prompt should be loaded
        assert len(versions) == 1
        assert "1.0.0" in versions
        assert "0.9.0" not in versions
    
    def test_render_user_prompt(self, temp_prompts_dir, sample_prompt_v1):
        """Test rendering a prompt template with variables."""
        manager = PromptManager(prompts_dir=temp_prompts_dir)
        
        prompt = manager.get_prompt("test_task")
        rendered = manager.render_user_prompt(prompt, input_text="Hello world")
        
        assert "Process this: Hello world" in rendered
        assert "{input_text}" not in rendered
    
    def test_render_missing_variable_raises_error(self, temp_prompts_dir, sample_prompt_v1):
        """Test that rendering without required variables raises an error."""
        manager = PromptManager(prompts_dir=temp_prompts_dir)
        
        prompt = manager.get_prompt("test_task")
        
        with pytest.raises(ValueError, match="Missing required template variable"):
            manager.render_user_prompt(prompt)
    
    def test_prompt_integrity_verification(self, temp_prompts_dir, sample_prompt_v1):
        """Test that prompt integrity is correctly verified."""
        manager = PromptManager(prompts_dir=temp_prompts_dir)
        
        prompt = manager.get_prompt("test_task")
        
        # Original prompt should pass integrity check
        assert manager.validate_prompt_integrity(prompt) is True
        
        # Modified prompt should fail integrity check
        prompt.system_prompt = "Modified system prompt"
        assert manager.validate_prompt_integrity(prompt) is False
    
    def test_prompt_hash_calculation(self, temp_prompts_dir, sample_prompt_v1):
        """Test that prompt hash is correctly calculated."""
        manager = PromptManager(prompts_dir=temp_prompts_dir)
        
        prompt = manager.get_prompt("test_task")
        
        # Hash should be a 64-character hex string (SHA256)
        assert len(prompt.prompt_hash) == 64
        assert all(c in '0123456789abcdef' for c in prompt.prompt_hash)
    
    def test_get_nonexistent_task(self, temp_prompts_dir, sample_prompt_v1):
        """Test getting a prompt for a task that doesn't exist."""
        manager = PromptManager(prompts_dir=temp_prompts_dir)
        
        prompt = manager.get_prompt("nonexistent_task")
        
        assert prompt is None
    
    def test_get_nonexistent_version(self, temp_prompts_dir, sample_prompt_v1):
        """Test getting a version that doesn't exist."""
        manager = PromptManager(prompts_dir=temp_prompts_dir)
        
        prompt = manager.get_prompt("test_task", version="9.9.9")
        
        assert prompt is None
    
    def test_reload_prompts(self, temp_prompts_dir, sample_prompt_v1):
        """Test reloading prompts from disk."""
        manager = PromptManager(prompts_dir=temp_prompts_dir)
        
        # Initially should have one version
        versions = manager.list_versions("test_task")
        assert len(versions) == 1
        
        # Add a new prompt file
        prompt_data = {
            "version": "2.0.0",
            "created_at": "2026-02-06T10:00:00Z",
            "created_by": "test@example.com",
            "status": "active",
            "task": "test_task",
            "description": "Major version update",
            "system_prompt": "You are a completely redesigned assistant.",
            "user_prompt_template": "New format: {input_text}",
            "validation": {},
            "metadata": {}
        }
        
        prompt_file = Path(temp_prompts_dir) / "test_task_v2.0.0.yaml"
        with open(prompt_file, 'w') as f:
            yaml.dump(prompt_data, f)
        
        # Reload prompts
        manager.reload_prompts()
        
        # Should now have two versions
        versions = manager.list_versions("test_task")
        assert len(versions) == 2
        assert "2.0.0" in versions
        
        # Latest should be 2.0.0
        prompt = manager.get_prompt("test_task")
        assert prompt.version == "2.0.0"
    
    def test_semantic_versioning_sorting(self, temp_prompts_dir):
        """Test that semantic versions are sorted correctly."""
        # Create versions in non-sequential order
        versions_to_create = ["1.0.0", "1.10.0", "1.2.0", "2.0.0", "1.1.0"]
        
        for version in versions_to_create:
            prompt_data = {
                "version": version,
                "created_at": "2026-02-04T10:00:00Z",
                "created_by": "test@example.com",
                "status": "active",
                "task": "versioning_test",
                "description": f"Version {version}",
                "system_prompt": f"System prompt for {version}",
                "user_prompt_template": "Template {input}",
                "validation": {},
                "metadata": {}
            }
            
            prompt_file = Path(temp_prompts_dir) / f"versioning_test_v{version}.yaml"
            with open(prompt_file, 'w') as f:
                yaml.dump(prompt_data, f)
        
        manager = PromptManager(prompts_dir=temp_prompts_dir)
        
        versions = manager.list_versions("versioning_test")
        
        # Should be sorted in descending order
        expected_order = ["2.0.0", "1.10.0", "1.2.0", "1.1.0", "1.0.0"]
        assert versions == expected_order
        
        # Latest should be 2.0.0
        latest = manager.get_prompt("versioning_test")
        assert latest.version == "2.0.0"
    
    def test_empty_prompts_directory(self, temp_prompts_dir):
        """Test behavior with an empty prompts directory."""
        manager = PromptManager(prompts_dir=temp_prompts_dir)
        
        prompt = manager.get_prompt("any_task")
        assert prompt is None
        
        versions = manager.list_versions("any_task")
        assert versions == []
    
    def test_multiple_tasks(self, temp_prompts_dir):
        """Test managing prompts for multiple different tasks."""
        # Create prompts for two different tasks
        tasks_data = [
            ("summarization", "1.0.0"),
            ("summarization", "1.1.0"),
            ("extraction", "1.0.0"),
            ("extraction", "2.0.0"),
        ]
        
        for task, version in tasks_data:
            prompt_data = {
                "version": version,
                "created_at": "2026-02-04T10:00:00Z",
                "created_by": "test@example.com",
                "status": "active",
                "task": task,
                "description": f"{task} v{version}",
                "system_prompt": f"System for {task}",
                "user_prompt_template": "Template {input}",
                "validation": {},
                "metadata": {}
            }
            
            prompt_file = Path(temp_prompts_dir) / f"{task}_v{version}.yaml"
            with open(prompt_file, 'w') as f:
                yaml.dump(prompt_data, f)
        
        manager = PromptManager(prompts_dir=temp_prompts_dir)
        
        # Check summarization task
        summ_versions = manager.list_versions("summarization")
        assert len(summ_versions) == 2
        summ_latest = manager.get_prompt("summarization")
        assert summ_latest.version == "1.1.0"
        
        # Check extraction task
        extr_versions = manager.list_versions("extraction")
        assert len(extr_versions) == 2
        extr_latest = manager.get_prompt("extraction")
        assert extr_latest.version == "2.0.0"


class TestPromptVersion:
    """Test suite for PromptVersion dataclass."""
    
    def test_prompt_version_attributes(self):
        """Test that PromptVersion correctly stores all attributes."""
        prompt = PromptVersion(
            version="1.0.0",
            task="test_task",
            system_prompt="System",
            user_prompt_template="User {var}",
            status="active",
            created_at="2026-02-04",
            created_by="test@example.com",
            description="Test description",
            validation={"max_tokens": 100},
            metadata={"approved_by": "manager"},
            prompt_hash="abc123"
        )
        
        assert prompt.version == "1.0.0"
        assert prompt.task == "test_task"
        assert prompt.status == "active"
        assert prompt.validation["max_tokens"] == 100
        assert prompt.metadata["approved_by"] == "manager"
        assert prompt.prompt_hash == "abc123"