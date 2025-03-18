from airflow import DAG
from airflow.operators.python import PythonOperator
from confluent_kafka import Producer
from faker import Faker
import logging
from datetime import datetime, timedelta
#from ..secret.secret import get_secret
import boto3
from botocore.exceptions import ClientError
import json


fake = Faker()
logger = logging.getLogger(__name__)



default_args = {
    'owner': 'Data Lab',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5)
}

def get_secret(secret_name,region_name):

    # secret_name = "MWAA_Secrets_V2"
    # region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = json.loads(get_secret_value_response['SecretString'])

    # Your code goes here.
    return secret

def create_kafka_producer(kafka_config):
    """
    Function to create a Kafka producer
    """
    producer = Producer(kafka_config)
    return producer

def generate_log():
    methods = ['GET', 'POST', 'DELETE', 'PUT']
    endpoints = ['/api/users', '/home', '/about', '/contact', '/services']
    status_codes = [200, 201, 301, 302, 400, 404, 500]

    user_agent = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.3',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.3',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.3',
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.3',
    ]

    # where is the traffic coming from
    referrers = [
        'https://example.com',
        'https://www.google.com',
        'https://www.bing.com',
        'https://www.yahoo.com',
        'https://www.duckduckgo.com',
        'https://www.baidu.com',
        'internal'
    ]

    ip = fake.ipv4()
    timestamp = datetime.now().strftime('%b %d %Y, %H:%M:%S')
    method = fake.random.choice(methods)
    endpoints = fake.random.choice(endpoints)
    status_code = fake.random.choice(status_codes)
    size= fake.random_int(1000, 15000)
    referrer = fake.random.choice(referrers)
    user_agent = fake.random.choice(user_agent)

    log_entry = f'{ip} - - [{timestamp}] "{method} {endpoints} HTTP/1.0" {status_code} {size} "{referrer}" "{user_agent}"'
    return log_entry

def delivery_report(err, msg):
    """
    Reports the failure or success of a message delivery.
    """
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def produce_logs(**context):
    """"    
    Function to generate logs and produce them to Kafka topic
    """
    secrets = get_secret('MWAA_Secrets_V2', 'us-east-1')
    kafka_config = {
        'bootstrap.servers': secrets['KAFKA_BOOTSTRAP_SERVER'],
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': secrets['KAFKA_SASL_USERNAME'],
        'sasl.password': secrets['KAFKA_SASL_PASSWORD'],
        'session.timeout.ms': 50000
    }

    producer = create_kafka_producer(kafka_config)
    topic = 'website_logs'

    for _ in range(15000):
        log = generate_log()
        try:
            producer.produce(topic, log.encode('utf-8'), on_delivery=delivery_report)
            producer.flush()
            logger.info(f'Log produced: {log}')
        except Exception as e:
            logger.error(f'Error producing log: {e}')
            raise e
        logger.info('Logs produced successfully for the {topic}')
    

dag = DAG(
    dag_id='log_producer',
    default_args=default_args,
    description='Generate logs',
    schedule_interval='*/5 * * * *',
    start_date= datetime(2025, 3, 17),
    catchup=False,
    tags=['logs','production','kafka']
)

produce_logs_task = PythonOperator(
    task_id='generate_and_produce_logs',
    python_callable=produce_logs,
    dag=dag
)