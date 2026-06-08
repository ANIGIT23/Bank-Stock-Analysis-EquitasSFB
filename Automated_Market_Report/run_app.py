from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
import pandas as pd
from typing import List

# Import the core logic functions
# We use try/except to handle both local and server paths
try:
    from .logic import robust_read_market_data
    from .Simple_Market_App import generate_full_package
except ImportError:
    from logic import robust_read_market_data
    from Simple_Market_App import generate_full_package

app = FastAPI()

# Setup paths relative to the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount static folders
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(os.path.join(TEMPLATES_DIR, "index.html"), "r") as f:
        return f.read()

@app.post("/upload_compare")
async def upload_compare(
    file1: UploadFile = File(...), 
    file2: UploadFile = File(...),
    exch: str = Form(...)
):
    path1 = os.path.join(UPLOADS_DIR, file1.filename)
    path2 = os.path.join(UPLOADS_DIR, file2.filename)

    with open(path1, "wb") as b1: shutil.copyfileobj(file1.file, b1)
    with open(path2, "wb") as b2: shutil.copyfileobj(file2.file, b2)

    try:
        # Process data exactly like Simple_Market_App.py
        data_map = {}
        raw_map = {}

        # Load Bank 1
        df1, bank1, _ = robust_read_market_data(path1)
        raw_map[bank1] = df1.copy()
        data_map[bank1] = df1.set_index('Date').resample('W-MON')['Lakhs'].mean().reset_index()

        # Load Bank 2
        df2, bank2, _ = robust_read_market_data(path2)
        raw_map[bank2] = df2.copy()
        data_map[bank2] = df2.set_index('Date').resample('W-MON')['Lakhs'].mean().reset_index()

        # Generate report package
        # We temporarily change directory to OUTPUT_DIR to save files there
        old_cwd = os.getcwd()
        os.chdir(OUTPUT_DIR)
        
        try:
            img_name, excel_name, links = generate_full_package(data_map, raw_map, exch)
        finally:
            os.chdir(old_cwd)

        return {
            "success": True, 
            "img_name": img_name, 
            "excel_name": excel_name, 
            "links": links
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
