FROM apache/airflow:2.10.5-python3.11

USER airflow

COPY airflow/requirements-airflow.txt /tmp/req-airflow.txt

RUN pip install --no-cache-dir \
    -r /tmp/req-airflow.txt \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.11.txt"
