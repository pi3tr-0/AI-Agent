import json
from typing import Dict, Any, Optional
from datetime import datetime


def combine_analysis_results(
    parsed_content: Dict[str, Any],
    financial_analysis: Any,
    sentiment_analysis: Any,
    leadership_analysis: Any,
    analyst_name: str,
    filename: str
) -> Dict[str, Any]:
    """
    Combine all analysis results into a single comprehensive JSON structure.
    
    Args:
        parsed_content: Full parsed content from fileParser
        financial_analysis: Financial analysis results
        sentiment_analysis: Sentiment analysis results  
        leadership_analysis: Leadership analysis results
        analyst_name: Name of the analyst
        filename: Original filename
        
    Returns:
        Combined analysis results as a dictionary
    """
    
    # Initialize the combined structure
    combined_results = {
        "metadata": {
            "analysis_timestamp": datetime.now().isoformat(),
            "analyst_name": analyst_name,
            "original_filename": filename,
            "analysis_version": "1.0"
        },
        "parsed_content": parsed_content,
        "financial_analysis": {},
        "sentiment_analysis": {},
        "leadership_analysis": {}
    }
    
    # Extract financial analysis results
    if financial_analysis and hasattr(financial_analysis, 'output'):
        try:
            if hasattr(financial_analysis.output, 'dict'):
                combined_results["financial_analysis"] = financial_analysis.output.dict()
            else:
                combined_results["financial_analysis"] = financial_analysis.output
        except Exception as e:
            combined_results["financial_analysis"] = {
                "error": f"Failed to serialize financial analysis: {str(e)}",
                "raw_output": str(financial_analysis.output) if hasattr(financial_analysis, 'output') else "No output"
            }
    else:
        combined_results["financial_analysis"] = {
            "error": "No financial analysis results available"
        }
    
    # Extract sentiment analysis results
    if sentiment_analysis and hasattr(sentiment_analysis, 'output'):
        try:
            if hasattr(sentiment_analysis.output, 'dict'):
                combined_results["sentiment_analysis"] = sentiment_analysis.output.dict()
            else:
                combined_results["sentiment_analysis"] = sentiment_analysis.output
        except Exception as e:
            combined_results["sentiment_analysis"] = {
                "error": f"Failed to serialize sentiment analysis: {str(e)}",
                "raw_output": str(sentiment_analysis.output) if hasattr(sentiment_analysis, 'output') else "No output"
            }
    else:
        combined_results["sentiment_analysis"] = {
            "error": "No sentiment analysis results available"
        }
    
    # Extract leadership analysis results
    if leadership_analysis and hasattr(leadership_analysis, 'output'):
        try:
            if hasattr(leadership_analysis.output, 'dict'):
                combined_results["leadership_analysis"] = leadership_analysis.output.dict()
            else:
                combined_results["leadership_analysis"] = leadership_analysis.output
        except Exception as e:
            combined_results["leadership_analysis"] = {
                "error": f"Failed to serialize leadership analysis: {str(e)}",
                "raw_output": str(leadership_analysis.output) if hasattr(leadership_analysis, 'output') else "No output"
            }
    else:
        combined_results["leadership_analysis"] = {
            "error": "No leadership analysis results available"
        }
    
    # Add summary section
    combined_results["summary"] = {
        "ticker": parsed_content.get("ticker", "Unknown"),
        "period": parsed_content.get("period", "Unknown"),
        "analyst_name": analyst_name,
        "analysis_status": "completed",
        "total_sections": 4  # parsed_content, financial, sentiment, leadership
    }
    
    return combined_results


def save_combined_results(
    combined_results: Dict[str, Any],
    filename: str,
    output_dir: str = "reports"
) -> str:
    """
    Save combined analysis results to a JSON file.
    
    Args:
        combined_results: Combined analysis results
        filename: Base filename (without extension)
        output_dir: Directory to save the file
        
    Returns:
        Path to the saved file
    """
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ticker = combined_results.get("summary", {}).get("ticker", "UNKNOWN")
    period = combined_results.get("summary", {}).get("period", "UNKNOWN").replace(" ", "_")
    
    output_filename = f"{ticker}_{period}_{timestamp}_combined_analysis.json"
    output_path = os.path.join(output_dir, output_filename)
    
    # Save to JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(combined_results, f, indent=2, ensure_ascii=False, default=str)
    
    return output_path


def get_combined_results_json(combined_results: Dict[str, Any]) -> str:
    """
    Convert combined results to JSON string for download.
    
    Args:
        combined_results: Combined analysis results
        
    Returns:
        JSON string representation
    """
    return json.dumps(combined_results, indent=2, ensure_ascii=False, default=str) 