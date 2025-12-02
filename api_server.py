import os
import shutil
import cv2
import uvicorn
import numpy as np
import traceback
import json
import time
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict, Any, Annotated

from src.pipeline.report_generator import generate_intelligence_summary
from src.utils.geo_utils import convert_pixels_to_geojson
from src.pipeline.change_detection import advanced_change_detection

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

from fastapi.responses import FileResponse

@app.get("/")
def root():
    return FileResponse("frontend/index.html")

@app.post("/api/v1/analyze_aoi")
async def analyze_area_of_interest(
    aoi_bounds_json: Annotated[str, Form()],
    image_before: Annotated[UploadFile, File()],
    image_after: Annotated[UploadFile, File()]
):
    try:
        try:
            aoi_bounds = json.loads(aoi_bounds_json)
            print(f"[API] Received analysis request for AOI: {aoi_bounds}")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid AOI bounds JSON.")

        upload_dir = f"data/uploads/{os.urandom(8).hex()}"
        os.makedirs(upload_dir, exist_ok=True)

        before_path = f"{upload_dir}/before_image.jpg"
        after_path = f"{upload_dir}/after_image.jpg"

        with open(before_path, "wb") as buffer:
            shutil.copyfileobj(image_before.file, buffer)
        with open(after_path, "wb") as buffer:
            shutil.copyfileobj(image_after.file, buffer)

        print(f"[API] Saved images to {upload_dir}")

        img_before_cv = cv2.imread(before_path)
        if img_before_cv is None:
            raise HTTPException(status_code=500, detail="Could not read 'before' image.")

        image_height, image_width, _ = img_before_cv.shape
        image_dims = (image_height, image_width)

        print("[API] Running advanced change detection...")
        change_mask, ssim_score, detected_contours = advanced_change_detection(before_path, after_path)
        
        mask_filename = "change_mask_latest.png"
        mask_save_path = f"static/{mask_filename}"
        cv2.imwrite(mask_save_path, change_mask)
        
        change_mask_url = f"http://127.0.0.1:8000/static/{mask_filename}"
        
        print("[API] Fusing data and scoring risk...")
        
        fused_data = []
        total_anomaly_area = 0
        
        for i, contour in enumerate(detected_contours):
            area = cv2.contourArea(contour)
            (x, y, w, h) = cv2.boundingRect(contour)
            total_anomaly_area += area

            anomaly_class = "Unknown Anomaly"
            if area > 1000: 
                anomaly_class = "Major Structure"
            elif area > 200: 
                anomaly_class = "Vehicle / Site"
            else: 
                anomaly_class = "Minor Anomaly / Movement"

            fused_data.append({
                "bbox_pixels": [x, y, x + w, y + h],
                "class": anomaly_class,
                "confidence": 0.9 + (np.log1p(area) / 10.0),
                "type": "New Anomaly",
                "area_pixels": int(area),
                "threat_level": "HIGH" if area > 1000 else "MEDIUM" if area > 200 else "LOW"
            })
        
        num_anomalies = len(fused_data)
        risk_score = min(max((num_anomalies * 1.5) + (total_anomaly_area / 1000.0) + ((1.0 - ssim_score) * 10.0), 0), 10)
        print(f"[API] Dynamic Risk Score: {risk_score:.2f}")

        print("[API] Converting pixel coordinates to GeoJSON...")
        anomalies_geojson = convert_pixels_to_geojson(
            fused_data, 
            aoi_bounds,
            image_dims
        )

        print("[API] Generating final report...")
        report_context = {
            "aoi_coordinates": aoi_bounds,
            "detected_anomalies": fused_data,
            "overall_ssim_score": ssim_score,
            "risk_score": risk_score,
            "num_anomalies": num_anomalies,
            "has_high_threat": any(d.get("threat_level") == "HIGH" for d in fused_data)
        }
        report_text = generate_intelligence_summary(report_context, risk_score)

        response_payload = {
            "report_summary": report_text,
            "change_mask_url": change_mask_url,
            "anomalies_geojson": anomalies_geojson,
            "image_bounds": aoi_bounds,
            "risk_score": risk_score,
            "fused_data": fused_data,
            "has_changes": num_anomalies > 0,
            "warning_message": f"⚠️ WARNING!! Noticed {num_anomalies} changes detected in AOI" if num_anomalies > 0 else "✅ No significant changes detected"
        }

        return response_payload

    except Exception as e:
        print(f"[API Error] {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analyze_aoi/monitor")
async def monitor_satellite_data(request: dict):
    try:
        location = request.get("location", "wagah")
        aoi_bounds = request.get("aoi_bounds")
        
        print(f"[Monitor] Starting real-time check for location: {location}")
        
        before_path = "data/sim_border_before.jpg"
        after_path = "data/sim_border_after_infiltration.jpg"
        
        if not os.path.exists(before_path) or not os.path.exists(after_path):
            raise HTTPException(status_code=500, detail="Simulation satellite images not found.")

        img_before = cv2.imread(before_path)
        img_after = cv2.imread(after_path)
        
        if img_before is None or img_after is None:
            raise HTTPException(status_code=500, detail="Could not read satellite images.")

        image_height, image_width, _ = img_before.shape
        image_dims = (image_height, image_width)

        print("[Monitor] Running real-time change detection...")
        change_mask, ssim_score, detected_contours = advanced_change_detection(before_path, after_path)
        
        mask_filename = f"realtime_mask_{location}_{int(time.time())}.png"
        mask_save_path = f"static/{mask_filename}"
        cv2.imwrite(mask_save_path, change_mask)
        change_mask_url = f"http://127.0.0.1:8000/static/{mask_filename}"
        
        print("[Monitor] Analyzing detected changes...")
        fused_data = []
        total_anomaly_area = 0
        
        for i, contour in enumerate(detected_contours):
            area = cv2.contourArea(contour)
            (x, y, w, h) = cv2.boundingRect(contour)
            total_anomaly_area += area
            
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
                "bbox_pixels": [x, y, x + w, y + h],
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
        
        print(f"[Monitor] Real-time analysis complete: {num_anomalies} anomalies, Risk: {risk_score:.1f}")
        
        anomalies_geojson = convert_pixels_to_geojson(
            fused_data, 
            aoi_bounds,
            image_dims
        )
        
        report_context = {
            "aoi_coordinates": aoi_bounds,
            "detected_anomalies": fused_data,
            "overall_ssim_score": ssim_score,
            "risk_score": risk_score,
            "num_anomalies": num_anomalies,
            "has_high_threat": high_threat_count > 0,
            "monitoring_location": location
        }
        report_text = generate_intelligence_summary(report_context, risk_score)
        
        response_data = {
            "report_summary": report_text,
            "change_mask_url": change_mask_url,
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
        print(f"[Monitor Error] {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Real-time monitoring error: {str(e)}")

if __name__ == "__main__":
    print("--- Starting DRISHTI-SHIELD API v5 (Real-Time Monitoring) on http://127.0.0.1:8000 ---")
    print("--- Ready for live satellite monitoring and anomaly detection ---")
    uvicorn.run(app, host="127.0.0.1", port=8000)
