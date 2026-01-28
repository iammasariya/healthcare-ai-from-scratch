"""
Example client for testing the Healthcare AI Service.

This demonstrates how to interact with the API programmatically.
"""

import requests
from datetime import datetime
from typing import Dict, Any


class ClinicalNoteClient:
    """
    Simple client for interacting with the clinical note service.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if the service is healthy.
        
        Returns:
            Health check response
        """
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def ingest_note(self, patient_id: str, note_text: str) -> Dict[str, Any]:
        """
        Ingest a clinical note.
        
        Args:
            patient_id: Unique patient identifier
            note_text: Clinical note content
            
        Returns:
            Response with audit_id and status
        """
        payload = {
            "patient_id": patient_id,
            "note_text": note_text
        }
        
        response = requests.post(
            f"{self.base_url}/ingest",
            json=payload
        )
        response.raise_for_status()
        return response.json()


def main():
    """
    Example usage of the client.
    """
    print("=" * 60)
    print("Healthcare AI Service - Example Client")
    print("=" * 60)
    print()
    
    # Initialize client
    client = ClinicalNoteClient()
    
    # Check health
    print("1. Checking service health...")
    try:
        health = client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Version: {health.get('version', 'unknown')}")
        print()
    except requests.exceptions.RequestException as e:
        print(f"   Error: {e}")
        print("   Is the service running? Start it with: uvicorn app.main:app")
        return
    
    # Example 1: Simple clinical note
    print("2. Ingesting a simple clinical note...")
    try:
        result = client.ingest_note(
            patient_id="PT-12345",
            note_text="Patient presents with acute onset headache. Vital signs stable."
        )
        print(f"   Audit ID: {result['audit_id']}")
        print(f"   Status: {result['status']}")
        print(f"   Received at: {result['received_at']}")
        print()
    except requests.exceptions.RequestException as e:
        print(f"   Error: {e}")
        print()
    
    # Example 2: Detailed clinical note
    print("3. Ingesting a detailed clinical note...")
    try:
        detailed_note = """
        Chief Complaint: Acute onset headache
        
        HPI: 45-year-old female presenting with severe headache that started 
        approximately 4 hours ago. Patient describes pain as throbbing, 
        localized to the frontal region, rated 8/10 in severity.
        
        Vital Signs:
        - BP: 120/80 mmHg
        - Pulse: 72 bpm
        - Temperature: 98.6°F
        - Respiratory Rate: 16/min
        
        Assessment: Likely migraine headache
        
        Plan: Prescribed sumatriptan 50mg, advised rest in dark room, 
        follow-up if symptoms persist beyond 24 hours.
        """
        
        result = client.ingest_note(
            patient_id="PT-67890",
            note_text=detailed_note
        )
        print(f"   Audit ID: {result['audit_id']}")
        print(f"   Status: {result['status']}")
        print()
    except requests.exceptions.RequestException as e:
        print(f"   Error: {e}")
        print()
    
    # Example 3: Demonstrate validation
    print("4. Testing validation (empty note - should fail)...")
    try:
        result = client.ingest_note(
            patient_id="PT-11111",
            note_text=""
        )
        print(f"   Unexpected success: {result}")
        print()
    except requests.exceptions.HTTPError as e:
        print(f"   Expected validation error: {e.response.status_code}")
        print(f"   Error details: {e.response.json()}")
        print()
    
    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)
    print()
    print("Key takeaways:")
    print("- Every request gets a unique audit_id for tracing")
    print("- Validation happens before processing")
    print("- Structured responses make integration easy")
    print("- This foundation is ready for AI extensions")


if __name__ == "__main__":
    main()
