import os
import shutil
import json
import time
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict, Any, Annotated
from PIL import Image, ImageDraw
import random
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

def create_placeholder_mask(filename="placeholder_mask.png"):
    """Create a simple placeholder mask image"""
    try:
        img = Image.new('RGB', (512, 512), color='black')
        draw = ImageDraw.Draw(img)
        
        for i in range(random.randint(1, 3)):
            x1 = random.randint(50, 300)
            y1 = random.randint(50, 300)
            x2 = x1 + random.randint(30, 100)
            y2 = y1 + random.randint(30, 100)
            draw.rectangle([x1, y1, x2, y2], fill='white')
        
        static_path = f"static/{filename}"
        img.save(static_path)
        return f"/static/{filename}"
    except:
        return "/static/placeholder_mask.png"

def process_border_surveillance_images():
    """Process actual border surveillance images using computer vision"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    before_path = os.path.join(base_dir, "data", "sim_border_before.jpg")
    after_path = os.path.join(base_dir, "data", "sim_border_after_infiltration.jpg")
    
    # Check if images exist
    if not os.path.exists(before_path) or not os.path.exists(after_path):
        raise FileNotFoundError(f"Simulation images not found: {before_path} or {after_path}")
    
    # Load images
    img_before = cv2.imread(before_path)
    img_after = cv2.imread(after_path)
    
    if img_before is None or img_after is None:
        raise ValueError("Could not load simulation images")
    
    # Resize images to same dimensions for comparison
    height, width = min(img_before.shape[0], img_after.shape[0]), min(img_before.shape[1], img_after.shape[1])
    img_before = cv2.resize(img_before, (width, height))
    img_after = cv2.resize(img_after, (width, height))
    
    # Convert to grayscale for analysis
    gray_before = cv2.cvtColor(img_before, cv2.COLOR_BGR2GRAY)
    gray_after = cv2.cvtColor(img_after, cv2.COLOR_BGR2GRAY)
    
    # Calculate SSIM score
    ssim_score, _ = ssim(gray_before, gray_after, full=True)
    
    # Compute difference
    diff = cv2.absdiff(gray_before, gray_after)
    
    # Apply threshold to get binary difference image
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    
    # Apply morphological operations to clean up noise
    kernel = np.ones((5,5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter and process contours
    detected_changes = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:  # Filter small noise
            x, y, w, h = cv2.boundingRect(contour)
            detected_changes.append({
                "area": int(area),
                "bbox": [int(x), int(y), int(w), int(h)],
                "contour": contour.tolist()
            })
    
    # Generate change mask image
    change_mask = np.zeros_like(gray_before)
    for change in detected_changes:
        contour_array = np.array(change["contour"], dtype=np.int32)
        cv2.fillPoly(change_mask, [contour_array], 255)
    
    # Save change mask
    static_dir = os.path.join(base_dir, "static")
    os.makedirs(static_dir, exist_ok=True)
    mask_filename = f"change_mask_{int(time.time())}.png"
    mask_path = os.path.join(static_dir, mask_filename)
    cv2.imwrite(mask_path, change_mask)
    
    return f"/static/{mask_filename}", ssim_score, detected_changes

app = FastAPI(title="DRISHTI-SHIELD API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("frontend/index.html")

def simple_change_detection_simulation():
    """Simulate change detection without any external dependencies"""
    import random
    
    # Generate random realistic anomaly data
    num_anomalies = random.randint(1, 4)
    detected_contours = []
    
    for i in range(num_anomalies):
        area = random.randint(300, 2000)
        x = random.randint(50, 400)
        y = random.randint(50, 300)
        w = random.randint(20, 80)
        h = random.randint(20, 60)
        
        detected_contours.append({
            "area": area, 
            "bbox": [x, y, w, h]
        })
    
    ssim_score = random.uniform(0.65, 0.85)
    return None, ssim_score, detected_contours

def convert_pixels_to_geojson_simple(pixel_data: list, aoi_bounds: dict):
    """Simplified geojson conversion"""
    features = []
    for i, item in enumerate(pixel_data):
        lat = aoi_bounds["south_west"]["lat"] + (i * 0.001)
        lng = aoi_bounds["south_west"]["lng"] + (i * 0.001)
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat]
            },
            "properties": {
                "type": item.get("type", "Unknown"),
                "class": item.get("class", "Unknown"),
                "confidence": item.get("confidence", 0.0)
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

def generate_simple_report(report_context: dict, risk_score: float) -> str:
    """Simple report generation without LLM"""
    num_anomalies = len(report_context.get("detected_anomalies", []))
    has_high_threat = report_context.get("has_high_threat", False)
    
    bluf = f"**BLUF (Bottom Line Up Front):** AI analysis has identified {num_anomalies} high-confidence anomalies."
    
    details = "**Detailed Analysis:**\n"
    if num_anomalies == 0:
        details += "* No significant changes detected in the specified AOI.\n"
    else:
        details += f"* WARNING: {num_anomalies} new anomalies detected.\n"
        if has_high_threat:
            details += "* HIGH THREAT LEVEL detected.\n"
    
    rec = "**Analyst Recommendation:**\n"
    if has_high_threat or risk_score > 8.0:
        rec += "* HIGH PRIORITY: Immediate review required."
    elif risk_score > 5.0:
        rec += "* MEDIUM PRIORITY: Monitor detected changes."
    else:
        rec += "* LOW PRIORITY: Continue routine monitoring."
    
    return f"{bluf}\n\n{details}\n\n{rec}"

@app.post("/api/v1/analyze_aoi_auto")
async def analyze_area_of_interest_auto(request: dict):
    """Automatic AOI analysis using pre-loaded simulation images"""
    try:
        aoi_bounds = request.get("aoi_bounds", {
            "north_east": {"lat": 31.6205, "lng": 74.8952},
            "south_west": {"lat": 31.6185, "lng": 74.8932}
        })
        
        # Use actual computer vision processing on simulation images
        change_mask_url, ssim_score, detected_contours = process_border_surveillance_images()
        
        fused_data = []
        total_anomaly_area = 0
        
        for i, contour_data in enumerate(detected_contours):
            area = contour_data["area"]
            total_anomaly_area += area
            
            anomaly_class = "Unknown Anomaly"
            if area > 1000: 
                anomaly_class = "Major Structure"
            elif area > 500: 
                anomaly_class = "Vehicle / Equipment"
            elif area > 200: 
                anomaly_class = "Personnel Movement"
            else: 
                anomaly_class = "Minor Activity"
            
            fused_data.append({
                "bbox_pixels": contour_data["bbox"],
                "class": anomaly_class,
                "confidence": min(0.95, 0.7 + (area / 2000.0)),
                "type": "Computer Vision Detection",
                "area_pixels": int(area),
                "threat_level": "HIGH" if area > 1000 else "MEDIUM" if area > 500 else "LOW"
            })
        
        num_anomalies = len(fused_data)
        risk_score = min(max((num_anomalies * 1.5) + (total_anomaly_area / 1000.0) + ((1.0 - ssim_score) * 10.0), 0), 10)
        
        anomalies_geojson = convert_pixels_to_geojson_simple(fused_data, aoi_bounds)
        
        report_context = {
            "aoi_coordinates": aoi_bounds,
            "detected_anomalies": fused_data,
            "overall_ssim_score": ssim_score,
            "risk_score": risk_score,
            "num_anomalies": num_anomalies,
            "has_high_threat": any(d.get("threat_level") == "HIGH" for d in fused_data)
        }
        report_text = generate_simple_report(report_context, risk_score)
        
        response_payload = {
            "report_summary": report_text,
            "change_mask_url": change_mask_url,
            "anomalies_geojson": anomalies_geojson,
            "image_bounds": aoi_bounds,
            "risk_score": risk_score,
            "fused_data": fused_data,
            "has_changes": num_anomalies > 0,
            "warning_message": f"⚠️ WARNING!! {num_anomalies} changes detected in border area" if num_anomalies > 0 else "✅ No significant changes detected",
            "analysis_method": "Computer Vision Processing",
            "ssim_similarity": round(ssim_score, 3)
        }
        
        return response_payload
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze_aoi/monitor")
async def monitor_satellite_data(request: dict):
    try:
        location = request.get("location", "wagah")
        aoi_bounds = request.get("aoi_bounds")
        
        # Use actual computer vision processing for monitoring
        change_mask_url, ssim_score, detected_contours = process_border_surveillance_images()
        
        # Use the generated mask URL for monitoring
        mask_url = change_mask_url
        
        fused_data = []
        for i, contour_data in enumerate(detected_contours):
            area = contour_data["area"]
            
            anomaly_class = "Unknown Change"
            threat_level = "LOW"
            
            if area > 1500:
                anomaly_class = "Large Structure/Vehicle"
                threat_level = "HIGH"
            elif area > 800:
                anomaly_class = "Military Equipment"  
                threat_level = "MEDIUM"
            elif area > 300:
                anomaly_class = "Personnel Movement"
                threat_level = "MEDIUM"
            else:
                anomaly_class = "Minor Activity"
                threat_level = "LOW"
            
            confidence = min(0.95, 0.7 + (area / 2000.0))
            
            detection = {
                "bbox_pixels": contour_data["bbox"],
                "class": anomaly_class,
                "confidence": confidence,
                "type": "Real-Time Detection",
                "area_pixels": int(area),
                "threat_level": threat_level
            }
            fused_data.append(detection)
        
        num_anomalies = len(fused_data)
        high_threat_count = sum(1 for d in fused_data if d["threat_level"] == "HIGH")
        medium_threat_count = sum(1 for d in fused_data if d["threat_level"] == "MEDIUM")
        
        risk_score = (high_threat_count * 4.0) + (medium_threat_count * 2.0) + (num_anomalies * 1.0)
        risk_score = min(max(risk_score, 0), 10)
        
        anomalies_geojson = convert_pixels_to_geojson_simple(fused_data, aoi_bounds)
        
        report_context = {
            "aoi_coordinates": aoi_bounds,
            "detected_anomalies": fused_data,
            "overall_ssim_score": ssim_score,
            "risk_score": risk_score,
            "num_anomalies": num_anomalies,
            "has_high_threat": high_threat_count > 0,
            "monitoring_location": location
        }
        report_text = generate_simple_report(report_context, risk_score)
        
        response_data = {
            "report_summary": report_text,
            "change_mask_url": mask_url,
            "anomalies_geojson": anomalies_geojson,
            "image_bounds": aoi_bounds,
            "risk_score": risk_score,
            "fused_data": fused_data,
            "has_changes": num_anomalies > 0,
            "warning_message": f"🚨 LIVE ALERT: {num_anomalies} anomalies detected at {location.upper()}" if num_anomalies > 0 else "✅ All clear - no changes detected",
            "monitoring_timestamp": time.time(),
            "location": location
        }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Real-time monitoring error: {str(e)}")

if __name__ == "__main__":
    print("--- Starting DRISHTI-SHIELD API v5 (Real-Time Monitoring) on http://127.0.0.1:8000 ---")
    print("--- Ready for live satellite monitoring and anomaly detection ---")
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
