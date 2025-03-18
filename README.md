# Realtime-Logs-Processing
Realtime Logs Processing With Apache Airflow, Kafka &amp; Elastisearch

# System Architecture

![1](https://res.cloudinary.com/vaibhav-codexpress/image/upload/v1742305141/diagram-export-18-03-2025-09_38_41_ivksxh.png)



airflow commands

```
airflow init db
airflow migrate
airflow db init
airflow migrate
airflow webserver -p 8180
airflow scheduler
```

```
export AIRFLOW_HOME=${pwd}
airflow users create \
--username admin \
--firstname Vaibhav \
--lastname Bansal \
--role Admin \
--email vaibhav.bansal2020@gmail.com
```
1. Store Secrets in AWS Secrets Manager
    a. KAFKA_SASL_USERNAME
    b. KAFKA_SASL_PASSWORD
    c. KAFKA_BOOTSTRAP_SERVER
    d. ELASTICSEARCH_URL
    e. ELASTICSEARCH_API_KEY

1. Create account in confluent kafka -> Create Environment -> Provision Cluster -> Create Topic
2. Get bootstrap Server from Cluster Settings in Kafka
3. Get bootstrap server url, username and password from API keys (Generate if not available)
4. Create environment and cluster in confluent kafka
5. Create account in elasticsearch
6. Create index in elasticserarch with partitions with a particular name in dags and get the elasticsearch url and api key to be stored in aws secrets manager
7. CREATE IAM USER
8. CREATE S3 Bucket
9. Go to AWS MANAGER APACHE AIRFLOW -> Create New Environment -> Link it to your dags -> Run Dag On Airflow
10. Configure the path for dag folder, S3 bucket, & requirements file
11. Create VPC and Add Secret Manager Read-Write policy to role in MWAA
