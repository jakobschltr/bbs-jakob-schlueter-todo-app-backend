FROM python:3.11-alpine

WORKDIR /app

RUN pip install flask==3.1.3

COPY app.py /app

ENTRYPOINT [ "python" ]
CMD ["app.py"]