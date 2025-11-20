"""JSON Compilation Module - Combines all task results"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class JSONCompiler:
    """Compiles results from all tasks into final JSON report"""
    
    def __init__(self):
        self.report = {
            "metadata": {},
            "task1_text_extraction": {},
            "task2_summary": {},
            "task3_legislative_sections": {},
            "task4_rule_checks": {}
        }
    
    def add_metadata(self, pdf_metadata: dict):
        """Add PDF metadata to report"""
        self.report["metadata"] = {
            "document_name": "Universal Credit Act 2025",
            "analysis_date": datetime.now().isoformat(),
            "pdf_info": pdf_metadata
        }
    
    def add_task1_result(self, extracted_text: str, pdf_path: str):
        """Add Task 1 results - Text Extraction"""
        self.report["task1_text_extraction"] = {
            "description": "Full text extracted from PDF",
            "source_file": str(pdf_path),
            "text_length": len(extracted_text),
            "status": "completed",
            "note": "Full text stored separately for brevity"
        }
    
    def add_task2_result(self, summary: dict):
        """Add Task 2 results - Summary"""
        self.report["task2_summary"] = {
            "description": "Act summarized in 5-10 bullet points",
            "summary_points": summary.get("summary", []),
            "status": "completed"
        }
    
    def add_task3_result(self, sections: dict):
        """Add Task 3 results - Legislative Sections"""
        self.report["task3_legislative_sections"] = {
            "description": "Key legislative sections extracted",
            "sections": sections,
            "status": "completed"
        }
    
    def add_task4_result(self, rule_checks: list):
        """Add Task 4 results - Rule Checks"""
        self.report["task4_rule_checks"] = {
            "description": "Six rule compliance checks applied",
            "total_rules": len(rule_checks),
            "passed": sum(1 for r in rule_checks if r.get("status") == "pass"),
            "failed": sum(1 for r in rule_checks if r.get("status") == "fail"),
            "checks": rule_checks,
            "status": "completed"
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate final report dictionary"""
        return self.report
    
    def save_to_file(self, output_path: str):
        """
        Save compiled report to JSON file
        
        Args:
            output_path: Path where JSON file should be saved
        """
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON with pretty formatting
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Report saved to: {output_file}")
        return output_file
    
    def save_extracted_text(self, text: str, output_dir: str):
        """
        Save extracted text to separate file
        
        Args:
            text: Full extracted text
            output_dir: Directory to save text file
        """
        text_file = Path(output_dir) / "extracted_text.txt"
        text_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"✓ Extracted text saved to: {text_file}")
        return text_file
