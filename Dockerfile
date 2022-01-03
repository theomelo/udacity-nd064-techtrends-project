FROM python:2.7.18-stretch
COPY ./techtrends /app
WORKDIR /app
RUN apt update && apt install python3-pip -y
RUN python -m pip install -r requirements.txt
RUN python init_db.py
EXPOSE 3111
CMD ["python", "app.py"]
