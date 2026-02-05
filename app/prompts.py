"""
Prompt management system with versioning and audit trails.

Treats prompts as first-class versioned artifacts, not strings in code.
"""

import hashlib
import yaml
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass
import logging


logger = logging.getLogger(__name__)


@dataclass
class PromptVersion:
    """
    A versioned prompt with metadata.
    
    Attributes:
        version: Semantic version (e.g., "1.0.0")
        task: What this prompt does (e.g., "clinical_summarization")
        system_prompt: Instructions for the model
        user_prompt_template: Template for user messages (may contain {placeholders})
        status: Lifecycle status (active, deprecated, retired)
        created_at: When this version was created
        created_by: Who created it
        description: Human-readable description
        validation: Validation rules for using this prompt
        metadata: Additional governance metadata
        prompt_hash: SHA256 hash of prompts for verification
    """
    version: str
    task: str
    system_prompt: str
    user_prompt_template: str
    status: str
    created_at: str
    created_by: str
    description: str
    validation: Dict
    metadata: Dict
    prompt_hash: str


class PromptManager:
    """
    Manages versioned prompts for LLM operations.
    
    Design principles:
    - Prompts are data, loaded from YAML files
    - Every prompt has a semantic version
    - Prompt content is hashed for integrity verification
    - Active prompts are cached for performance
    - Changes require new versions, not in-place edits
    """
    
    def __init__(self, prompts_dir: str = "prompts"):
        """
        Initialize prompt manager.
        
        Args:
            prompts_dir: Directory containing prompt YAML files
        """
        self.prompts_dir = Path(prompts_dir)
        self.prompts_dir.mkdir(exist_ok=True)
        self._cache: Dict[str, Dict[str, PromptVersion]] = {}
        self._load_all_prompts()
    
    def _load_all_prompts(self) -> None:
        """
        Load all prompt files from disk into cache.
        
        Prompts are organized by task, then by version.
        Only 'active' prompts are loaded into the cache.
        """
        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory {self.prompts_dir} does not exist")
            return
        
        for yaml_file in self.prompts_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                # Skip non-active prompts
                if data.get('status') != 'active':
                    logger.info(f"Skipping non-active prompt: {yaml_file.name}")
                    continue
                
                # Calculate hash for integrity
                prompt_hash = self._calculate_hash(
                    data['system_prompt'],
                    data['user_prompt_template']
                )
                
                prompt_version = PromptVersion(
                    version=data['version'],
                    task=data['task'],
                    system_prompt=data['system_prompt'],
                    user_prompt_template=data['user_prompt_template'],
                    status=data['status'],
                    created_at=data['created_at'],
                    created_by=data['created_by'],
                    description=data['description'],
                    validation=data.get('validation', {}),
                    metadata=data.get('metadata', {}),
                    prompt_hash=prompt_hash,
                )
                
                # Cache by task and version
                task = data['task']
                if task not in self._cache:
                    self._cache[task] = {}
                
                self._cache[task][data['version']] = prompt_version
                
                logger.info(
                    f"Loaded prompt: {task} v{data['version']} "
                    f"(hash: {prompt_hash[:8]}...)"
                )
                
            except Exception as e:
                logger.error(f"Failed to load prompt from {yaml_file}: {e}")
    
    def get_prompt(
        self,
        task: str,
        version: Optional[str] = None
    ) -> Optional[PromptVersion]:
        """
        Get a prompt by task and version.
        
        Args:
            task: The task name (e.g., "clinical_summarization")
            version: Specific version to use (e.g., "1.0.0")
                    If None, returns the latest version
        
        Returns:
            PromptVersion if found, None otherwise
        """
        if task not in self._cache:
            logger.warning(f"No prompts found for task: {task}")
            return None
        
        if version:
            prompt = self._cache[task].get(version)
            if not prompt:
                logger.warning(f"Prompt not found: {task} v{version}")
            return prompt
        
        # Return latest version (highest semantic version)
        versions = list(self._cache[task].keys())
        if not versions:
            return None
        
        latest = self._get_latest_version(versions)
        return self._cache[task][latest]
    
    def list_versions(self, task: str) -> List[str]:
        """
        List all available versions for a task.
        
        Returns versions in descending order (newest first).
        """
        if task not in self._cache:
            return []
        
        versions = list(self._cache[task].keys())
        return sorted(versions, key=self._version_sort_key, reverse=True)
    
    def render_user_prompt(
        self,
        prompt_version: PromptVersion,
        **kwargs
    ) -> str:
        """
        Render user prompt template with provided variables.
        
        Args:
            prompt_version: The prompt version to render
            **kwargs: Variables to substitute in template
        
        Returns:
            Rendered prompt string
        
        Example:
            prompt = manager.get_prompt("clinical_summarization")
            rendered = manager.render_user_prompt(
                prompt,
                note_text="Patient presents with..."
            )
        """
        try:
            return prompt_version.user_prompt_template.format(**kwargs)
        except KeyError as e:
            raise ValueError(
                f"Missing required template variable: {e}. "
                f"Template requires: {self._extract_template_vars(prompt_version.user_prompt_template)}"
            )
    
    def validate_prompt_integrity(self, prompt_version: PromptVersion) -> bool:
        """
        Verify prompt integrity by recalculating hash.
        
        This detects if prompts were modified after loading.
        In production, this would trigger alerts.
        """
        current_hash = self._calculate_hash(
            prompt_version.system_prompt,
            prompt_version.user_prompt_template
        )
        is_valid = current_hash == prompt_version.prompt_hash
        
        if not is_valid:
            logger.error(
                f"Prompt integrity check failed for {prompt_version.task} v{prompt_version.version}. "
                f"Expected hash: {prompt_version.prompt_hash[:8]}..., "
                f"Actual hash: {current_hash[:8]}..."
            )
        
        return is_valid
    
    @staticmethod
    def _calculate_hash(system_prompt: str, user_prompt_template: str) -> str:
        """
        Calculate SHA256 hash of prompt content.
        
        Used for integrity verification and change detection.
        """
        content = system_prompt + user_prompt_template
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    @staticmethod
    def _get_latest_version(versions: List[str]) -> str:
        """Get the latest semantic version from a list."""
        return max(versions, key=PromptManager._version_sort_key)
    
    @staticmethod
    def _version_sort_key(version: str) -> tuple:
        """
        Convert semantic version to sortable tuple.
        
        "1.2.3" -> (1, 2, 3)
        """
        try:
            parts = version.split('.')
            return tuple(int(p) for p in parts)
        except (ValueError, AttributeError):
            logger.warning(f"Invalid semantic version format: {version}")
            return (0, 0, 0)
    
    @staticmethod
    def _extract_template_vars(template: str) -> List[str]:
        """
        Extract variable names from a template string.
        
        Example: "Hello {name}, you are {age}" -> ["name", "age"]
        """
        import re
        return re.findall(r'\{(\w+)\}', template)
    
    def reload_prompts(self) -> None:
        """
        Reload prompts from disk.
        
        Use this to pick up prompt changes without restarting the service.
        In production, this would be triggered by a configuration reload endpoint.
        """
        logger.info("Reloading prompts from disk")
        self._cache.clear()
        self._load_all_prompts()
        logger.info(f"Reloaded {sum(len(v) for v in self._cache.values())} prompts")


# Global prompt manager instance
_prompt_manager: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """Get or create global prompt manager instance."""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager