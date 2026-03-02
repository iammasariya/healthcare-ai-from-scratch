"""
HELM / MedHELM Adapter for Healthcare AI System (Optional)

This module provides adapters to use our LLM service with Stanford HELM
and MedHELM-compatible workflows.
Only needed if you want to run comprehensive benchmark evaluations.

Installation:
    pip install -U "crfm-helm[summarization,medhelm]"

Usage:
    See examples/helm_evaluation_example.py
"""

from typing import Optional

# HELM imports (only imported if HELM is installed)
try:
    from helm.proxy.models.model import Model
    from helm.common.request import Request, RequestResult
    from helm.benchmark.scenarios.scenario import Scenario, Instance
    HELM_AVAILABLE = True
except ImportError:
    HELM_AVAILABLE = False
    # Define dummy classes for type hints
    class Model:
        pass
    class Request:
        pass
    class RequestResult:
        pass
    class Scenario:
        pass
    class Instance:
        pass

from app.evaluation import GoldenDataset


class ClinicalModel(Model):
    """
    HELM adapter for our clinical LLM service.
    
    This allows HELM to use our LLM service while maintaining
    all our reliability patterns (retries, cost tracking, etc.)
    """
    
    def __init__(self, model_name: str = "custom-clinical-model"):
        """
        Initialize the clinical model adapter.
        
        Args:
            model_name: Name to register with HELM
        """
        if not HELM_AVAILABLE:
            raise ImportError(
                'HELM / MedHELM is not installed. Install with: '
                'pip install -U "crfm-helm[summarization,medhelm]"'
            )

        super().__init__(model_name)
        self.llm_service = None
        
    def _get_llm_service(self):
        """
        Lazy load LLM service.

        Importing here avoids forcing full app configuration at module import
        time for users who only want to inspect benchmark availability.
        """
        if self.llm_service is None:
            from app.llm import get_llm_service
            self.llm_service = get_llm_service()
        return self.llm_service
    
    def make_request(self, request: Request) -> RequestResult:
        """
        Make a request to our LLM service (HELM interface).
        
        Args:
            request: HELM request object
            
        Returns:
            RequestResult with the model's response
        """
        llm_service = self._get_llm_service()
        
        # Extract parameters from HELM request
        prompt = request.prompt
        temperature = request.temperature if hasattr(request, 'temperature') else 0.3
        
        # Call our LLM service
        try:
            response = llm_service.summarize_clinical_note(
                note_text=prompt,
                temperature=temperature
            )
            
            # Convert to HELM result format
            from helm.common.request import GeneratedOutput, Token
            
            result = RequestResult(
                success=True,
                cached=False,
                request_time=response.latency_ms / 1000.0,  # Convert to seconds
                completions=[
                    GeneratedOutput(
                        text=response.summary,
                        logprob=0.0,  # We don't have logprobs
                        tokens=[Token(text=response.summary, logprob=0.0)]
                    )
                ]
            )
            
            return result
            
        except Exception as e:
            # Return failure result
            return RequestResult(
                success=False,
                cached=False,
                error=str(e)
            )


class ClinicalSummarizationScenario(Scenario):
    """
    HELM scenario for clinical summarization evaluation.
    
    This converts our golden dataset to HELM format.
    """
    
    name = "clinical_summarization"
    description = "Evaluates clinical note summarization quality using curated examples"
    tags = ["clinical", "summarization", "healthcare"]
    
    def __init__(self, dataset_path: str = "evaluation_datasets/clinical_summarization_golden.json"):
        """
        Initialize scenario with golden dataset.
        
        Args:
            dataset_path: Path to golden dataset JSON file
        """
        super().__init__()
        self.dataset_path = dataset_path
    
    def get_instances(self) -> list:
        """
        Load instances from golden dataset.
        
        Returns:
            List of HELM Instance objects
        """
        if not HELM_AVAILABLE:
            raise ImportError("HELM / MedHELM is not installed")
        
        # Load our golden dataset
        dataset = GoldenDataset(self.dataset_path)
        dataset.load()
        
        # Convert to HELM instances
        instances = []
        for example in dataset.examples:
            instance = Instance(
                input=example.input_text,
                references=[example.expected_output],
                id=example.id,
                # Pass metadata as split (for filtering)
                split=example.metadata.get("clinical_specialty", "general")
            )
            instances.append(instance)
        
        return instances


def check_helm_availability() -> bool:
    """
    Check if HELM is installed and available.
    
    Returns:
        True if HELM is available, False otherwise
    """
    return HELM_AVAILABLE


def register_clinical_model():
    """
    Register our clinical model with HELM's model registry.
    
    Call this before running HELM evaluations.
    """
    if not HELM_AVAILABLE:
        raise ImportError(
            'HELM / MedHELM is not installed. Install with: '
            'pip install -U "crfm-helm[summarization,medhelm]"'
        )
    
    from helm.proxy.services.model_registry import register_model
    
    register_model(
        "custom-clinical-model",
        lambda: ClinicalModel("custom-clinical-model")
    )
    
    print("✓ Registered custom-clinical-model with HELM")


def convert_golden_dataset_to_helm(
    dataset_path: str,
    output_path: str
) -> None:
    """
    Convert our golden dataset to HELM format for use with HELM tools.
    
    Args:
        dataset_path: Path to our golden dataset JSON
        output_path: Path to save HELM-formatted dataset
    """
    dataset = GoldenDataset(dataset_path)
    dataset.load()
    
    # Convert to HELM format
    helm_data = {
        "name": "clinical_summarization",
        "description": "Clinical note summarization evaluation",
        "instances": []
    }
    
    for example in dataset.examples:
        helm_instance = {
            "id": example.id,
            "input": example.input_text,
            "references": [example.expected_output],
            "metadata": example.metadata
        }
        helm_data["instances"].append(helm_instance)
    
    # Save
    import json
    with open(output_path, 'w') as f:
        json.dump(helm_data, f, indent=2)
    
    print(f"✓ Converted {len(dataset.examples)} examples to HELM format")
    print(f"  Saved to: {output_path}")


if __name__ == "__main__":
    # Quick test
    print(f"HELM Available: {check_helm_availability()}")
    
    if HELM_AVAILABLE:
        print("\nHELM / MedHELM Integration:")
        print("- ClinicalModel: Adapter for our LLM service")
        print("- ClinicalSummarizationScenario: Uses our golden dataset")
        print("\nTo use:")
        print('1. Install: pip install -U "crfm-helm[summarization,medhelm]"')
        print("2. Run: python examples/helm_evaluation_example.py")
    else:
        print("\nHELM / MedHELM not installed. To enable benchmark integration:")
        print('  pip install -U "crfm-helm[summarization,medhelm]"')
