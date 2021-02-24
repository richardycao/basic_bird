import airflow
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from src.data.producer import test_function, generate_stream
from src.data.consumer import retrieve_stream

args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(1),
    'provide_context': False
}

dag2 = DAG(
    dag_id='dag2',
    default_args=args,
    schedule_interval='@hourly',
    catchup=False
)

task3 = PythonOperator(
    task_id='consumer',
    python_callable=retrieve_stream,
    dag=dag2
)

task3