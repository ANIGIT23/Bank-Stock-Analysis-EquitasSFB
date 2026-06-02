from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
from logic import process_market_data

app = FastAPI()

# Create directories if they don't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("output", exist_ok=True)

# Serve the output folder so images can be displayed
app.mount("/output", StaticFiles(directory="output"), name="output")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("templates/index.html", "r") as f:
        return f.read()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join("uploads", file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        report_path, peaks = process_market_data(file_path, "output")
        # Format peaks for JSON response
        peak_list = []
        for _, row in peaks.iterrows():
            peak_list.append({
                "Date": row['Date'].strftime('%Y-%m-%d'),
                "Lakhs": row['Lakhs']
            })
            
        return {"success": True, "peaks": peak_list}
    except Exception as e:
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 App starting on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
