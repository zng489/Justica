FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED 1
WORKDIR /project
COPY ./requirements.txt /project/requirements.txt

EXPOSE 5002

RUN pip install --no-cache-dir --upgrade -r /project/requirements.txt

COPY . /project
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload", "--reload-dir", "/project"]
