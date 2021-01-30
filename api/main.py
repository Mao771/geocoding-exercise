import uvicorn
from fastapi import BackgroundTasks, FastAPI, File, UploadFile, Form, Query
from fastapi.staticfiles import StaticFiles

import uuid
import logging
import pandas as pd
from definitions import CSV_DIRECTORY
from api import GeocodeTask


app = FastAPI()
task = GeocodeTask()
logger = logging.getLogger(__name__)
app.mount("/csv", StaticFiles(directory=CSV_DIRECTORY), name="csv")


@app.post("/run")
async def geo_encode(background_tasks: BackgroundTasks, csv_file: UploadFile = File(...),
                     columns: str = Form(...)):
    if task.in_progress():
        return {'success': False, 'error': 'There is not finished task. Please wait until it will be finished.'}

    try:
        if csv_file and columns:
            input_dataframe = pd.read_csv(csv_file.file, delimiter=";")
            input_columns = columns.split(',')
        else:
            raise ValueError('Please, provide input data as a form-data')
        task_id = uuid.uuid4()
        background_tasks.add_task(task.run, input_dataframe, input_columns, task_id)
        return {'success': True, 'message': 'Task successfully started. Id: {}'.format(task_id)}
    except Exception as e:
        logger.error(str(e))
        return {'success': False, 'error': str(e)}


@app.get("/status")
async def task_status(task_id: str = Query(None)):
    try:
        return task.task_status(task_id)
    except ValueError as e:
        return {"success": False, "error": str(e)}


@app.get("/stats")
async def task_stats():
    return task.stats()


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0")
