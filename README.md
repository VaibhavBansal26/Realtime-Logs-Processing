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

1. Create account in confluent kafka
2. Get bootstrap server url, username and password
3. Create environment and cluster in confluent kafka
4. Create account in elasticsearch
5. Create index in elasticserarch with partitions with a particular name in dags and get the elasticsearch url and api key to be stored in aws secrets manager
6. CREATE IAM USER
7. CREATE S3 Bucket
8. Go to AWS MANAGER APACHE AIRFLOW -> Create New Environment -> Link it to your dags -> Run Dag On Airflow
9. Configure the path for dag folder, S3 bucket, & requirements file
10. Create VPC
