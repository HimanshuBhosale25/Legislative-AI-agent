"""
NIYAMR AI - 48-Hour Internship Assignment
Universal Credit Act 2025 AI Agent
Main Orchestrator - Runs all 4 tasks
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

from src.pdf_extractor import extract_text_from_pdf, get_pdf_metadata
from src.gemini_analyzer import GeminiAnalyzer
from src.json_compiler import JSONCompiler


def main():
    """Main execution function"""
    print("=" * 60)
    print("NIYAMR AI - Universal Credit Act 2025 Analyzer")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Define paths
    pdf_path = Path("data/ukpga_20250022_en.pdf")
    output_dir = Path("output")
    output_json = output_dir / "final_report.json"
    
    # Check if PDF exists
    if not pdf_path.exists():
        print(f"Error: PDF not found at {pdf_path}")
        print(f"Please place the Universal Credit Act 2025 PDF in the 'data' folder")
        sys.exit(1)
    
    # Initialize components
    compiler = JSONCompiler()
    
    try:
        # TASK 1: Extract Text from PDF
        print("\n[Task 1] Extracting text from PDF...")
        extracted_text = extract_text_from_pdf(str(pdf_path))
        pdf_metadata = get_pdf_metadata(str(pdf_path))
        
        print(f"Extracted {len(extracted_text)} characters")
        print(f"PDF has {pdf_metadata.get('total_pages', 0)} pages")
        
        # Add to compiler
        compiler.add_metadata(pdf_metadata)
        compiler.add_task1_result(extracted_text, pdf_path)
        
        # Save extracted text separately
        compiler.save_extracted_text(extracted_text, str(output_dir))
        
        # TASK 2: Summarize the Act
        print("\n[Task 2] Summarizing the Act...")
        analyzer = GeminiAnalyzer()
        summary = analyzer.summarize_act(extracted_text)
        
        print(f"Generated {len(summary.get('summary', []))} summary points")
        compiler.add_task2_result(summary)
        
        # TASK 3: Extract Legislative Sections
        print("\n[Task 3] Extracting legislative sections...")
        sections = analyzer.extract_legislative_sections(extracted_text)
        
        print(f"Extracted {len(sections)} legislative sections")
        compiler.add_task3_result(sections)
        
        # TASK 4: Apply Rule Checks
        print("\n[Task 4] Applying 6 rule checks...")
        rule_checks = analyzer.apply_rule_checks(extracted_text)
        
        passed = sum(1 for r in rule_checks if r.get("status") == "pass")
        print(f"Completed {len(rule_checks)} rule checks")
        print(f"  - Passed: {passed}/{len(rule_checks)}")
        compiler.add_task4_result(rule_checks)
        
        # FINAL: Generate and Save Report
        print("\n[Final] Generating JSON report...")
        compiler.save_to_file(str(output_json))
        
        print("\n" + "=" * 60)
        print("✓ Analysis Complete!")
        print(f"✓ Final report: {output_json}")
        print(f"✓ Extracted text: {output_dir / 'extracted_text.txt'}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
