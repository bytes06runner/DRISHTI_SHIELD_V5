import json
import os
from openai import OpenAI

def generate_intelligence_summary(report_context: dict, risk_score: float) -> str:
    
    system_prompt = f"""
    You are DRISHTI-SHIELD, an AI Intelligence Analyst (Tier 2) for the Indian Armed Forces.
    Your mission is to provide a concise, factual, and actionable summary
    of satellite imagery analysis from a user-defined Area of Interest (AOI).
    
    Input data is a JSON object containing AOI coordinates, a list of detected
    anomalies (fused from ViT and change detection), and a risk score.
    
    Format your response in 3 sections:
    1. **BLUF (Bottom Line Up Front):** A single-sentence summary of the most critical finding.
    2. **Detailed Analysis:** A bulleted list of significant changes, referencing their class.
       Mention the *number* of new anomalies.
    3. **Analyst Recommendation:** A single, actionable recommendation.
    
    Be formal, precise, and use military-style language.
    """
    
    user_prompt = f"Analyze the following data and generate the report:\n\n{json.dumps(report_context, indent=2)}"

    try:
        
        print("[LLM] Generating simulated report...")
        
        num_anomalies = len(report_context.get("detected_anomalies", []))
        aoi = report_context.get("aoi_coordinates", {})
        
        has_high_threat = report_context.get("has_high_threat", False)
        threat_warning = " [HIGH THREAT DETECTED]" if has_high_threat else ""
        
        bluf = f"**BLUF (Bottom Line Up Front):** AI analysis of AOI [Lat: {aoi.get('south_west',{}).get('lat'):.4f}, Lng: {aoi.get('south_west',{}).get('lng'):.4f}] has identified {num_anomalies} high-confidence anomalies, indicating new activity{threat_warning}."

        details = "**Detailed Analysis:**\n"
        if num_anomalies == 0:
            details += "* No significant changes or new objects detected in the specified AOI.\n"
            details += "* All clear - monitoring continues.\n"
        else:
            threat_levels = {}
            for d in report_context.get("detected_anomalies", []):
                level = d.get('threat_level', 'UNKNOWN')
                if level not in threat_levels:
                    threat_levels[level] = []
                threat_levels[level].append(d.get('class', 'Unknown'))
            
            details += f"* ⚠️  WARNING: {num_anomalies} new anomalies detected in satellite imagery.\n"
            
            for level, classes in threat_levels.items():
                unique_classes = ", ".join(list(set(classes)))
                details += f"* {level} threat level: {unique_classes} ({len(classes)} detected).\n"
                
            details += f"* Structural Similarity Score of {report_context.get('overall_ssim_score', 0):.2f} indicates temporal changes.\n"
            details += "* Exact coordinates provided for each anomaly on map overlay.\n"

        rec = "**Analyst Recommendation:**\n"
        if has_high_threat or risk_score > 8.0:
            rec += "* ⚠️  HIGH PRIORITY: Immediate review required. Large structures detected."
        elif risk_score > 5.0:
            rec += "* MEDIUM PRIORITY: Monitor detected changes. Correlate with intelligence reports."
        elif num_anomalies > 0:
            rec += "* LOW PRIORITY: Log detections for trend analysis. Continue monitoring."
        else:
            rec += "* ROUTINE: No action required. Area remains stable."

        return f"{bluf}\n\n{details}\n\n{rec}"

    except Exception as e:
        print(f"[Error] LLM report generation failed: {e}")
        return "ERROR: Failed to generate intelligence report."

if __name__ == "__main__":
    mock_fused_data = [
        {"type": "new_object", "class": "vehicle_convoy", "count": 12, "location": "Sector 4B"},
        {"type": "structure_change", "class": "building", "area_sq_m": 500, "location": "Sector 4B"},
    ]
    mock_risk_score = 9.2
    
    report = generate_intelligence_summary(mock_fused_data, mock_risk_score)
    print("\n--- GENERATED INTELLIGENCE REPORT ---")
    print(report)
