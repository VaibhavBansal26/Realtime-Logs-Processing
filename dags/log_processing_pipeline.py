from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from confluent_kafka import Consumer,KafkaException
from elasticsearch import Elasticsearch
import json
import logging
import re
import boto3
#from ..secret.secret import get_secret
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

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


# def parse_log_entry(log_entry):
#     """
#     Function to parse a log entry
#     """
#     log_pattern = r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>.*)\] "(?P<method>\w+) (?P<endpoint>[\w/]+) (?P<protocol>[\w/\.]+)'
#     match = re.match(log_pattern, log_entry)
#     if not match:
#         logger.error(f'Failed to parse log entry: {log_entry}')
#         return None
#     log = match.groupdict()

#     try:
#         parse_timestamp = datetime.strptime(log['timestamp'], '%d/%b/%Y:%H:%M:%S')
#         log['timestamp'] = parse_timestamp.isoformat()
#     except Exception as e:
#         logger.error(f'Failed to parse timestamp: {e}')
#         return None
#     return log

def parse_log_entry(log_entry):
    """
    Function to parse a log entry
    """
    log_pattern = r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>.*)\] "(?P<method>\w+) (?P<endpoint>[\w/]+) (?P<protocol>[\w/\.]+)'
    match = re.match(log_pattern, log_entry)
    if not match:
        logger.error(f'Failed to parse log entry: {log_entry}')
        return None
    log = match.groupdict()

    try:
        # Updated format string to match "Mar 18 2025, 14:26:59"
        parse_timestamp = datetime.strptime(log['timestamp'], '%b %d %Y, %H:%M:%S')
        log['timestamp'] = parse_timestamp.isoformat()
    except Exception as e:
        logger.error(f'Failed to parse timestamp: {e}')
        return None
    return log


def consume_and_index_logs():
    """
    Function to consume logs from Kafka and index them in Elasticsearch
    """
    # Get the secret
    secret = get_secret('MWAA_Secrets_V2','us-east-1')
    kafka_consumer_config = {
        'bootstrap.servers': secret['KAFKA_BOOTSTRAP_SERVER'],
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': secret['KAFKA_SASL_USERNAME'],
        'sasl.password': secret['KAFKA_SASL_PASSWORD'],
        'group.id': 'logs-consumer',
        'auto.offset.reset': 'latest'
    }

    # Connect to Elasticsearch
    es_config = {
        'hosts': secret['ELASTICSEARCH_URL'],
        'api_key': secret['ELASTICSEARCH_API_KEY']
    }

    consumer = Consumer(kafka_consumer_config)
    es = Elasticsearch(**es_config)
    topic = 'website_logs'
    consumer.subscribe([topic])

    # Before we start consuming messages, we need to make sure that the index exists
    try:
        data_stream_index_name = 'website_logs'
        if not es.indices.exists(data_stream_index_name):
            es.indices.create(data_stream_index_name)
            logger.info(f'Index created: {data_stream_index_name}')
    except Exception as e:
        logger.error(f'Error creating index: {e}')
    

    try:
        logs = []
        while True:
            message = consumer.poll(timeout=1.0) # Poll for new messages, wait for 1 second to receive messages from Kafka
            if message is None:
                continue
            if message.error():
                if message.error().code() == KafkaException._PARTITION_EOF:
                    logger.warning('End of partition reached {0}/{1}'
                                    .format(message.topic(), message.partition()))
                else:
                    logger.error(f'Error occurred: {message.error().str()}')
            else:
                log_entry = message.value().decode('utf-8')
                parsed_log = parse_log_entry(log_entry)

                if parsed_log:
                    logs.append(parsed_log)
                
                # index when 15000 logs are collected
                if len(logs) >= 2000:
                    actions = [
                        {
                            '_op_type': 'index',
                            '_index': data_stream_index_name,
                            '_source': log
                        }
                        for log in logs
                        ]
                    success, failed = es.bulk(actions, refresh=True)
                    logger.info(f'Indexed {success} logs, failed to index {len(failed)} logs')
                    logs = []
    except Exception as e:
        logger.error(f'Failed to index log: {e}')
    
    # index remaining logs
    try:
        if logs:
            actions = [
                {
                    '_op_type': 'index',
                    '_index': data_stream_index_name,
                    '_source': log
                }
                for log in logs
            ]
            es.bulk(actions, refresh=True)
            logs = []
    except Exception as e:
        logger.error(f'Failed to index log: {e}')
    finally:
        consumer.close()
        es.close()
        logger.info('Consumer closed')


default_args = {
    'owner': 'Data Lab',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5)
}

dag = DAG(
    dag_id='log_consumer',
    default_args=default_args,
    description='Generate logs',
    schedule_interval='*/5 * * * *',
    start_date= datetime(2025, 3, 17),
    catchup=False,
    tags=['logs','production','kafka']
)

consume_logs_task = PythonOperator(
    task_id='generate_and_consume_logs',
    python_callable=consume_and_index_logs,
    dag=dag
)