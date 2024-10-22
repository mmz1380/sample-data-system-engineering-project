FROM python:3.11-slim

WORKDIR /app

COPY requirements_data.txt /app/

RUN pip install --no-cache-dir -r requirements_data.txt

COPY data_generator.py /app/

CMD ["python", "data_generator.py"]
