FROM python:3.10.8

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY db ./db
COPY core ./core
COPY models ./models
COPY services ./services
COPY api ./api
COPY main.py .

EXPOSE 8000

CMD ["python3", "main.py"]