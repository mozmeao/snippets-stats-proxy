FROM python:3-slim

EXPOSE 8000

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app

CMD ["./run.sh"]
