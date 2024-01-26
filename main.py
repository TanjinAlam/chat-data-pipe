import codecs
from typing import Union
import pandas as pd
from fastapi import BackgroundTasks, FastAPI, UploadFile, File
from schemas.request_data import request_data
from utils.help import insert_to_mongodb, find_data, update_data
from fastapi.responses import JSONResponse

app = FastAPI()
import csv

MAX_FILE_SIZE_MB = 1000  # Set your desired maximum file size in megabytes


@app.get("/")
async def read_root():
    return await find_data('chat-data', 'chat-documents')


@app.post("/upload")
async def upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    csvReader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
    
    file_size = file.file._file.__sizeof__()  # Getting the file size in bytes
    if file_size > (MAX_FILE_SIZE_MB * 1024 * 1024):
        return JSONResponse(content=f"File size exceeds the maximum allowed size of {MAX_FILE_SIZE_MB}MB", status_code=400)
    csv.field_size_limit(MAX_FILE_SIZE_MB * 1024 * 1024)
    
    df = pd.DataFrame(list(csvReader))
    
    background_tasks.add_task(insert_to_mongodb, df, 'chat-data', 'chat-documents')
    return "file is uploading"

@app.post("/")
async def read_root(body: request_data):
    return await update_data(body,'chat-data', 'chat-documents')