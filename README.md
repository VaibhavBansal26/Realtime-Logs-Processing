# Realtime-Logs-Processing
Realtime Logs Processing With Apache Airflow, Kafka &amp; Elastisearch

# System Architecture

![1](https://res.cloudinary.com/vaibhav-codexpress/image/upload/v1742305141/diagram-export-18-03-2025-09_38_41_ivksxh.png)

# Demo Video

[![demo](http://img.youtube.com/vi/ZcIbqeIAC0Y/0.jpg)]("https://www.youtube.com/watch?v=ZcIbqeIAC0Y")

# Screenshots

![2](https://res.cloudinary.com/vaibhav-codexpress/image/upload/v1742321981/Screenshot_2025-03-18_at_2.15.20_PM_vefnzk.png)

![3](https://res.cloudinary.com/vaibhav-codexpress/image/upload/v1742321980/Screenshot_2025-03-18_at_2.15.28_PM_oej9fh.png)

![4](https://res.cloudinary.com/vaibhav-codexpress/image/upload/v1742321979/Screenshot_2025-03-18_at_2.16.07_PM_qtza3x.png)

![5](https://res.cloudinary.com/vaibhav-codexpress/image/upload/v1742321978/Screenshot_2025-03-18_at_2.17.09_PM_easzch.png)

![6](https://res.cloudinary.com/vaibhav-codexpress/image/upload/v1742321978/Screenshot_2025-03-18_at_2.16.21_PM_r9n6ii.png)



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

2. Create account in confluent kafka -> Create Environment -> Provision Cluster -> Create Topic
3. Get bootstrap Server from Cluster Settings in Kafka
4. Get bootstrap server url, username and password from API keys (Generate if not available)
5. Create environment and cluster in confluent kafka
6. Create account in elasticsearch
7. Create index in elasticserarch with partitions with a particular name in dags and get the elasticsearch url and api key to be stored in aws secrets manager
8. CREATE IAM USER
9. CREATE S3 Bucket
10. Go to AWS MANAGER APACHE AIRFLOW -> Create New Environment -> Link it to your dags -> Run Dag On Airflow
11. Configure the path for dag folder, S3 bucket, & requirements file
12. Create VPC and Add Secret Manager Read-Write policy to role in MWAA
