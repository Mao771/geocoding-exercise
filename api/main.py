from fastapi import BackgroundTasks, FastAPI, File, UploadFile, Form, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import uuid
import logging
import pandas as pd
from definitions import CSV_DIRECTORY
from typing import List, Optional
from api import GeocodeTask

app = FastAPI()
task = GeocodeTask()
logger = logging.getLogger(__name__)
app.mount("/csv", StaticFiles(directory=CSV_DIRECTORY), name="csv")


class Data(BaseModel):
    url: str
    columns: List[str]


@app.post("/run")
async def geo_encode(background_tasks: BackgroundTasks, data: Data = None, csv_file: UploadFile = File(None),
                     columns: str = Form(None)):
    if task.in_progress():
        return {'success': False, 'error': 'There is not finished task. Please wait until it will be finished.'}
    else:
        try:
            if data:
                input_dataframe = pd.read_csv(data.url, delimiter=";")
                input_columns = data.columns
            elif csv_file and columns:
                input_dataframe = pd.read_csv(csv_file.file, delimiter=";")
                input_columns = columns.split(',')
            else:
                raise ValueError('Please, provide input data whether as a JSON body or as a form-data')
            task_id = uuid.uuid4()
            print(input_dataframe.head())
            background_tasks.add_task(task.run, input_dataframe, input_columns, task_id)
            return {'success': True, 'message': 'Task successfully started. Id: {}'.format(task_id)}
        except Exception as e:
            logger.error(str(e))
            return {'success': False, 'error': str(e)}


@app.post("/status")
async def task_status(task_id: str = Query(None)):
    try:
        return {'success': True, 'message': task.task_status(task_id)}
    except Exception as e:
        logger.error(str(e))
        return {'success': False, 'error': 'Some error occurred, please, try again later.'}


@app.get("/stats")
async def task_stats():
    return task.stats()
