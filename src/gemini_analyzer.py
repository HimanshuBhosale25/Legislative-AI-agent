"""Tasks 2-4: Gemini AI Analysis Module - LangChain Implementation"""

import os
import json
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field  # Use regular pydantic, not v1
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ActSummary(BaseModel):
    """Schema for Task 2: Act Summary"""
    purpose: str = Field(description="Purpose of the Act")
    key_definitions: str = Field(description="Key definitions in the Act")
    eligibility: str = Field(description="Eligibility criteria")
    obligations: str = Field(description="Key obligations")
    enforcement: str = Field(description="Enforcement elements")


class LegislativeSections(BaseModel):
    """Schema for Task 3: Key Legislative Sections"""
    definitions: str = Field(description="Key term definitions from the Act")
    obligations: str = Field(description="Obligations outlined in the Act")
    responsibilities: str = Field(description="Responsibilities of parties involved")
    eligibility: str = Field(description="Eligibility criteria specified")
    payments: str = Field(description="Payment calculation or entitlement structure")
    penalties: str = Field(description="Penalties and enforcement mechanisms")
    record_keeping: str = Field(description="Record-keeping or reporting requirements")


class RuleCheck(BaseModel):
    """Schema for Task 4: Individual Rule Check"""
    rule: str = Field(description="The rule being checked")
    status: str = Field(description="Pass or fail status")
    evidence: str = Field(description="Evidence or section reference")
    confidence: int = Field(description="Confidence score 0-100")


class GeminiAnalyzer:
    """Analyzer for Universal Credit Act using LangChain + Gemini AI"""
    
    def __init__(self, api_key: str = None):
        """Initialize LangChain Gemini client"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        # Initialize LangChain ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0.1,
        )
    
    def summarize_act(self, text: str) -> dict:
        """
        Task 2: Summarize the Act in 5-10 bullet points
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            Dictionary with summary bullet points
        """
        prompt = f"""
Analyze the following Universal Credit Act 2025 and provide a summary in exactly 5 bullet points covering:

1. Purpose - What is the main purpose of this Act?
2. Key Definitions - What are the most important terms defined?
3. Eligibility - Who is eligible under this Act?
4. Obligations - What are the key obligations?
5. Enforcement - What enforcement mechanisms exist?

Be concise and specific. Extract actual section references where possible.

TEXT:
{text[:20000]}
"""
        
        # Use structured output WITHOUT method parameter
        structured_llm = self.llm.with_structured_output(ActSummary)
        
        try:
            summary = structured_llm.invoke(prompt)
            
            # Format as bullet points
            return {
                "summary": [
                    f"Purpose: {summary.purpose}",
                    f"Key Definitions: {summary.key_definitions}",
                    f"Eligibility: {summary.eligibility}",
                    f"Obligations: {summary.obligations}",
                    f"Enforcement: {summary.enforcement}"
                ]
            }
        except Exception as e:
            # Fallback if structured output fails
            print(f"Warning: Structured output failed, using text parsing: {e}")
            response = self.llm.invoke(prompt)
            lines = [line.strip() for line in response.content.split('\n') if line.strip()]
            return {"summary": lines[:10]}
    
    def extract_legislative_sections(self, text: str) -> dict:
        """
        Task 3: Extract key legislative sections
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            Dictionary with seven legislative categories
        """
        prompt = f"""
Extract the following sections from the Universal Credit Act 2025. Be specific and include section numbers.

Return a JSON object with these exact keys:
- "definitions": Key terms defined in the Act
- "obligations": Obligations stated in the Act
- "responsibilities": Responsibilities of the administering authority
- "eligibility": Eligibility criteria for claimants
- "payments": Payment calculation or entitlement structure
- "penalties": Enforcement or penalty mechanisms
- "record_keeping": Record-keeping or reporting requirements

TEXT:
{text[:20000]}
"""
        
        # Use structured output without method parameter
        structured_llm = self.llm.with_structured_output(LegislativeSections)
        
        try:
            sections = structured_llm.invoke(prompt)
            
            # Convert Pydantic model to dict
            return sections.model_dump()
        except Exception as e:
            print(f"Warning: Structured output failed: {e}")
            # Fallback with default values
            return {
                "definitions": "Error extracting definitions",
                "obligations": "Error extracting obligations",
                "responsibilities": "Error extracting responsibilities",
                "eligibility": "Error extracting eligibility",
                "payments": "Error extracting payments",
                "penalties": "Error extracting penalties",
                "record_keeping": "Error extracting record_keeping"
            }
    
    def apply_rule_checks(self, text: str) -> List[dict]:
        """
        Task 4: Apply 6 rule checks to validate the Act
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            List of rule check results
        """
        rules = [
            "Act must define key terms",
            "Act must specify eligibility criteria",
            "Act must specify responsibilities of the administering authority",
            "Act must include enforcement or penalties",
            "Act must include payment calculation or entitlement structure",
            "Act must include record-keeping or reporting requirements"
        ]
        
        results = []
        
        # Create structured output model for each rule
        structured_llm = self.llm.with_structured_output(RuleCheck)
        
        for rule in rules:
            prompt = f"""
Analyze if the Universal Credit Act 2025 meets this requirement:
"{rule}"

Determine:
1. Status: "pass" or "fail"
2. Evidence: Specific section reference or evidence from the Act
3. Confidence: Score from 0-100 indicating confidence in this assessment

Return JSON with keys: rule, status, evidence, confidence

TEXT:
{text[:20000]}
"""
            
            try:
                rule_result = structured_llm.invoke(prompt)
                results.append(rule_result.model_dump())
            except Exception as e:
                # Fallback if structured output fails
                print(f"Warning: Rule check failed for '{rule}': {e}")
                results.append({
                    "rule": rule,
                    "status": "error",
                    "evidence": f"Analysis failed: {str(e)}",
                    "confidence": 0
                })
        
        return results
