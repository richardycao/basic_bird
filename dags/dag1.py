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

dag = DAG(
    dag_id='dag1',
    default_args=args,
    schedule_interval='@once',
    catchup=False
)

task1 = PythonOperator(
    task_id='test_function',
    python_callable=test_function,
    dag=dag
)

task2 = PythonOperator(
    task_id='producer',
    python_callable=generate_stream,
    dag=dag
)

task3 = PythonOperator(
    task_id='consumer',
    python_callable=retrieve_stream,
    dag=dag
)

task1 >> task2 >> task3