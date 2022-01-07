FROM python:3.9-alpine
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip install requests
CMD ["python", "app.py"]