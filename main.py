import codecs
from typing import Union
import pandas as pd
from fastapi import BackgroundTasks, FastAPI, UploadFile, File

from utils.help import insert_to_mongodb, find_data

app = FastAPI()
import csv


@app.get("/")
async def read_root():
    return find_data('chat-data', 'chat-documents')


@app.post("/upload")
def upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    csvReader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
    df = pd.DataFrame(list(csvReader))
    background_tasks.add_task(insert_to_mongodb(df, 'chat-data', 'chat-documents'))
    return "file is uploading"

