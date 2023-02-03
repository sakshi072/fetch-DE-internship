import boto3
import json
from datetime import date
import psycopg2
from dotenv import load_dotenv
import os
from anonymizeip import anonymize_ip
import random

# fetching message from SQS localstack using boto3 client for SQS with aws connection credentials. 
def read_SQS(queue_url):
    # Creating a client for SQS in using boto3 to fetch messages from aws local
    # Using credentials from .env file as environment variable 
    sqs_client = boto3.client("sqs", 
                            region_name=os.environ.get('region_name'), 
                            endpoint_url = os.environ.get('endpoint_url'), 
                            aws_access_key_id = os.environ.get('aws_access_key_id'), 
                            aws_secret_access_key = os.environ.get('aws_secret_access_key'), 
                            aws_session_token = os.environ.get('aws_session_token'))

    # storing the message received from sqs client for the queue_url in localstack 
    response = sqs_client.receive_message(QueueUrl = queue_url)

    # parsing the received message to extract only body tag which consists of fields from our postgres user_logins table 
    for message in response.get("Messages", []):
        message_body = message["Body"]
        # loading the json in a dictionary which will be used to extract individual fields with key, value pairs. 
        body = json.loads(message_body)
    return body

# Extracting individual fields as given in the table's DDL and storing in variables to pass into the Postgres' insert command. 
def get_database_fields(body):

    user_id = body['user_id']
    device_type = body['device_type']
    masked_ip = body['ip']
    masked_device_id = body['device_id']
    locale = body['locale']
    app_version = ''.join(body['app_version'].split('.'))
    create_date = date.today()
    
     # masking ip and device_id using custom function by adding integer to all the units places of the delimeter separated individual strings in ips and devide ids. 
    masked_ip = masked_ip.split('.')
    for i in range(len(masked_ip)):
        # adding either 8 or 9 to the -1th index of each delimeter separated part of the ip
        if masked_ip[i][-1] == '9':
            masked_ip[i] = masked_ip[i][:-1] + '8'
        else:
            masked_ip[i] = masked_ip[i][:-1] + '9'
    masked_ip = '.'.join(masked_ip)
   
    masked_device_id = masked_device_id.split('-')
    for i in range(len(masked_device_id)):
        # adding either 8 or 9 to the -1th index of each delimeter separated part of the device-id
        if masked_device_id[i][-1] == '9':
            masked_device_id[i] = masked_device_id[i][:-1] + '8'
        else:
            masked_device_id[i] = masked_device_id[i][:-1] + '9'
    masked_device_id = '-'.join(masked_device_id)

    return [user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date]

# Connecting to postgres and inserting values into the table user_logins
def postgres_Insert(user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date):
    # try and except command lets handle any failure which can break the application
    try:
        # connecting to the postgres server 
        connection = psycopg2.connect(user = os.environ.get('user'),
                                    password = os.environ.get('password'),
                                    host = os.environ.get('host'),
                                    port = os.environ.get('port'),
                                    database = os.environ.get('database'))
        
        # Cursor allows the python code to execute postgres commands in a database session
        cursor = connection.cursor()
        # query to be executed in the postgres database for table user_logins
        insert_Query = "INSERT into user_logins(user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date) VALUES ('{}', '{}', '{}', '{}', '{}', {}, '{}')".format(user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
        # Cursor executing the above query 
        cursor.execute(insert_Query)

        # Commiting the execution of the query 
        connection.commit()
        # Closing the connection opened at the start of the function
        connection.close()
        print("Inserted")

    # handling any error that might break the application in connection or execution of the postgres try block
    except (Exception, psycopg2.Error) as error:
        print("Error while inserting data into the postgresSQL", error)

# Main function that runs on triggering the python program
if __name__== "__main__":

    #loading AWS SQS and Postgres credentials stored as environment variables
    load_dotenv()
    # reading the sqs message from the localstack queue 
    SQS_message = read_SQS(os.environ.get('QueueUrl'))
    # extracting all the fields from the message body received as per the DDL command of the postgres user_logins table
    user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date = get_database_fields(SQS_message)
    # Instering into the postgres table
    postgres_Insert(user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
