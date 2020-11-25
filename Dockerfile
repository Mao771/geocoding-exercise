FROM python:3.7

RUN pip install -r requirements.txt

EXPOSE 80

COPY ./api /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
