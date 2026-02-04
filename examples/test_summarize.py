"""
Example client for testing the /summarize endpoint (Post 2).

This demonstrates how to:
- Call the LLM-powered summarization endpoint
- Handle successful responses with metrics
- Handle failure responses gracefully
- Track costs across multiple requests
"""

import requests
import json
from typing import Dict, Any, List
from datetime import datetime


class SummarizeClient:
    """Client for interacting with the summarize endpoint."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.total_cost = 0.0
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
    
    def summarize_note(self, patient_id: str, note_text: str) -> Dict[str, Any]:
        """
        Summarize a clinical note.
        
        Args:
            patient_id: Patient identifier
            note_text: Clinical note text
            
        Returns:
            Response dictionary with summary and metrics
        """
        url = f"{self.base_url}/summarize"
        payload = {
            "patient_id": patient_id,
            "note_text": note_text
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            self.total_requests += 1
            
            if data.get("status") == "completed":
                self.successful_requests += 1
                if data.get("llm_metrics"):
                    self.total_cost += data["llm_metrics"]["cost_usd"]
            else:
                self.failed_requests += 1
            
            return data
            
        except requests.exceptions.RequestException as e:
            self.total_requests += 1
            self.failed_requests += 1
            return {
                "error": f"Request failed: {str(e)}",
                "status": "failed"
            }
    
    def print_response(self, response: Dict[str, Any]) -> None:
        """Pretty print a response."""
        print("\n" + "="*80)
        print(f"Audit ID: {response.get('audit_id')}")
        print(f"Status: {response.get('status')}")
        print(f"Patient ID: {response.get('patient_id')}")
        
        if response.get("summary"):
            print(f"\nSummary:\n{response['summary']}")
        
        if response.get("llm_metrics"):
            metrics = response["llm_metrics"]
            print(f"\nMetrics:")
            print(f"  Model: {metrics['model']}")
            print(f"  Tokens: {metrics['tokens_used']}")
            print(f"  Latency: {metrics['latency_ms']:.2f}ms")
            print(f"  Cost: ${metrics['cost_usd']:.6f}")
        
        if response.get("error"):
            print(f"\nError: {response['error']}")
        
        print("="*80)
    
    def print_stats(self) -> None:
        """Print statistics about all requests."""
        print("\n" + "="*80)
        print("SESSION STATISTICS")
        print("="*80)
        print(f"Total Requests: {self.total_requests}")
        print(f"Successful: {self.successful_requests}")
        print(f"Failed: {self.failed_requests}")
        if self.total_requests > 0:
            success_rate = (self.successful_requests / self.total_requests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Cost: ${self.total_cost:.6f}")
        if self.successful_requests > 0:
            avg_cost = self.total_cost / self.successful_requests
            print(f"Average Cost per Success: ${avg_cost:.6f}")
        print("="*80 + "\n")


def main():
    """Run example requests."""
    client = SummarizeClient()
    
    print("Healthcare AI Service - Summarization Client (Post 2)")
    print("="*80)
    
    # Example 1: Simple headache case
    print("\n[Example 1: Tension Headache]")
    response1 = client.summarize_note(
        patient_id="PT-12345",
        note_text="""
        Patient presents with acute onset headache. Denies trauma. 
        Vital signs: BP 120/80, HR 72, Temp 98.6F. 
        Neurological exam normal. 
        Assessment: Tension headache. 
        Plan: Acetaminophen 500mg PO PRN. Follow up if symptoms worsen or persist beyond 48 hours.
        """
    )
    client.print_response(response1)
    
    # Example 2: More complex case with medications
    print("\n[Example 2: Hypertension Follow-up]")
    response2 = client.summarize_note(
        patient_id="PT-67890",
        note_text="""
        64-year-old male presents for hypertension follow-up. 
        Currently taking Lisinopril 20mg daily, Hydrochlorothiazide 25mg daily.
        Reports good medication adherence. No side effects.
        Vital signs: BP 128/82, HR 68, Temp 98.4F, Weight 180 lbs.
        Lab results: Creatinine 1.0, Potassium 4.2, Sodium 138.
        Assessment: Hypertension, well-controlled on current regimen.
        Plan: Continue current medications. Recheck labs in 6 months. 
        Encouraged dietary sodium restriction and regular exercise.
        """
    )
    client.print_response(response2)
    
    # Example 3: Diabetes management
    print("\n[Example 3: Diabetes Management]")
    response3 = client.summarize_note(
        patient_id="PT-11223",
        note_text="""
        52-year-old female with Type 2 Diabetes Mellitus presents for routine follow-up.
        Currently on Metformin 1000mg twice daily.
        Home glucose readings: fasting 110-130, post-prandial 140-160.
        HbA1c today: 7.2% (previous 7.8%).
        Vital signs: BP 118/76, HR 74, Temp 98.6F, BMI 28.5.
        Denies polyuria, polydipsia, or hypoglycemic episodes.
        Foot exam: No ulcers, normal monofilament sensation bilaterally.
        Assessment: Type 2 DM, improving control.
        Plan: Continue Metformin. Encouraged weight loss goal of 10 pounds. 
        Recheck HbA1c in 3 months. Referred to nutritionist for dietary counseling.
        """
    )
    client.print_response(response3)
    
    # Example 4: Very short note (edge case)
    print("\n[Example 4: Brief Note]")
    response4 = client.summarize_note(
        patient_id="PT-99999",
        note_text="Patient seen for medication refill. No complaints. All stable."
    )
    client.print_response(response4)
    
    # Print session statistics
    client.print_stats()
    
    # Example of checking if LLM is enabled before making requests
    print("\nChecking service health...")
    try:
        health_response = requests.get(f"{client.base_url}/health")
        health_data = health_response.json()
        print(f"Service Status: {health_data.get('status')}")
        print(f"Version: {health_data.get('version')}")
    except Exception as e:
        print(f"Health check failed: {e}")


if __name__ == "__main__":
    main()