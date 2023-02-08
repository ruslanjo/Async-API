FROM python:3.10.8

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/tests/functional"

COPY requirements.txt .


RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY db ./db
COPY core ./core
COPY models ./models
COPY services ./services
COPY dao ./dao
COPY api ./api
COPY tests ./tests
COPY main.py .

EXPOSE 8000

CMD ["python3", "main.py"]