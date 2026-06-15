FROM python:3.11-alpine

RUN pip install flask==3.1.3

WORKDIR /app

COPY app.py /app

EXPOSE 5000

ENTRYPOINT [ "python" ]
CMD ["app.py"]
