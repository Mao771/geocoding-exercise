FROM python:3.7
COPY . geocoding-exercise
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 80
COPY ./api api
WORKDIR geocoding-exercise
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]
