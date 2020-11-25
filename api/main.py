from fastapi import BackgroundTasks, FastAPI, File, UploadFile, Query

import uuid
import pandas as pd
from typing import List
from api import GeocodeTask

app = FastAPI()
task = GeocodeTask()


@app.post("/run/")
async def geo_encode(csv_file: UploadFile = File(...), columns: List[str] = Query(None)):
    if task.in_progress():
        return {'success': False, 'error': 'There is not finished task. Please wait until it will be finished.'}
    else:
        try:
            df = pd.read_csv(csv_file.file, delimiter=";")
            task_id = uuid.uuid4()
            BackgroundTasks.add_task(task.run, df, columns, task_id)
            return {'success': True, 'message': 'Task successfully started. Id: {}'.format(task_id)}
        except:
            return {'success': False, 'error': 'File must be in a csv format'}


@app.post("/status")
async def task_status(task_id: int = Query(None)):
    try:
        return {'success': True, 'message': task.task_status(task_id)}
    except:
        return {'success': False, 'error': 'Some error occurred, please, try again later.'}
