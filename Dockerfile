FROM python:2.7.18-stretch
COPY ./techtrends /app
WORKDIR /app
RUN pip install -U pip wheel setuptools && \
    pip install -r requirements.txt && \
    python init_db.py
EXPOSE 3111
CMD ["python", "app.py"]