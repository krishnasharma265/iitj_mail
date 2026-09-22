FROM python:3.12

WORKDIR /smtp-server

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY /smtp-server .

CMD ["python","-u","server.py"]