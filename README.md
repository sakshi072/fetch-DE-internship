# Data Engineer Internship Application

## About the Application 
Application runs to fetch messages from AWS SQS Queue, parse them to extract useful data as per the fields in the schema of the database (postreSQL) and inserts the values from the messages to this database (postreSQL). The application has 3 components - 
* AWS SQS Queue
* Python function (potential AWS lambda function)
* Database - PostreSQL (Potential AWS RDS Database)

The flow is as - messages will be commited to the SQS queue. These messages will be read by the lambda function. Lambda function will be triggered when a new messages is queued in SQS queue. Lambda function will then extract, clean and upload this data to the database. 

## Development Decisions - 
#### -Reading the messages from the queue- 
The docker images run using docker-compose up with a yaml file having both the localstack’s image and Postgres database’s image. docker-compose up will run the server and host the applications on ports specified in the yaml.
As the AWS Queue is made available via a custom localstack image with pre-loaded data, the data can be fetched using boto3 which gives access to AWS services. A boto3 client can be created for the service AWS SQS with dummy credentials and default region for the given scenario. In production, valid credentials should be used as a configuration file. 

#### -Data structures used- 
I have used JSON to load the body message from the SQS queue and parsed it to extract useful information as per the schema of the database table provided in the question. Variables are used to store extarcted data. It is passed in a list to the inserting in the postgres function. 

#### Masking the PII data so that duplicate values can be identified -
Masking of the PII data can be done in multiple ways to also identify duplicate values like - 
* Hash function
* Tokenization
* Anonymization

I have used Anonymization and Hash function to mask the PII data ip and device_id. 
For the ip I have used anonymizeip that anonymizing IP addresses. Both IPv4 and IPv6 addresses are supported. 
For the device_id I have used a custom hashing function where I am extarcting last 4 digits of the id and adding random integers to it. 
This is generates masked PII data ip which is a one way making and cannot be reveresed once performed. 

#### -What will be your strategy for connecting and writing to Postgres - 
For connecting to the Postgres, I have used psycopg2 package in Python. It was designed for heavily multi-threaded applications that create and destroy lots of cursors and make a large number of concurrent “INSERT”s or “UPDATE”s. I have used a credentials to first make a connection with the database server. With this connection string, using a cursor method, I have inserted values extarcted from the SQS queue into the Postgres and committed the changes to reflect them in the database. Once the data is inserted I have closed the connection. 

#### -Running the application - 
Currently the application can be run from a terminal in three window. 
* One window will run the docker to host the localstack for AWS SQS which will provide with the pre-loaded data to pull. 
* Second window will run the PostgreSQL to query the database and check user_logins table for an insertion on running the application.
* Third window will run the application with a python command. 

On running the python script, the application will fetch the data from the AWS SQS queue, parse it and store it in the postgres user_logins table.

###### -The other solution for running this application which is not implemented is - 
The application can be hosted in a cloud service provider so that is available and scalable for instance, AWS.  The AWS SQS can be used for the messaging queue and AWS RDS can provision and run the Postgres database. The functionality of the application can be run using the AWS lambda function in this scenario. The lambda function can have the python script which will pull the SQS messages, parse them and store in local variable. Then a connection can be established with the RDS Postgres database using its credentials. With the local variable storing the message, useful information as per the schema of the database can be extracted and inserted using connection string and cursors. This entire section can be executed in AWS lambda. Further, a trigger can be set on AWS lambda. As and when a new message is pushed into the SQS queue, it will trigger this python application to store tuples with message information in the Postgres databases. 

## Components of the project
The project consists of following files - 

* .env - consists of dummy credentials for AWS and good credentials for postgres to connect to the AWS SQS and Database
* docker-compose.yaml - consists of both the images of localstack for AWS SQS and postgres for database. It is configuration file to run both the images together.
* program.py - consists of the functionality of the entire application that uses credentials from .env file
* requirements.txt - this has all the python packages and libraries requirements for the project

## Python Installations 
Install python and pip in your system. Below links can be used for the initial setup -
- Macos- https://docs.python-guide.org/starting/install3/osx/ 
- Linux - https://docs.python-guide.org/starting/install3/linux/
- Windows - https://www.tutorialspoint.com/how-to-install-python-in-windows

Homebrew Install for mac- https://brew.sh/ 

## Executing the script  
```
terminal one to keep running application 
docker compose up

terminal two - 
brew install postgresql@13
psql -d postgres -U postgres -p 5432 -h localhost -W
select * from user_logins;

terminal three - 
pip3 install -r ./requirements.txt
python3 program.py  
```
on running the python script a statement will be printed on successful run - "Inserted". Check the postgres table for the inserted tuple.

## Sample Output
```
postgres=# select * from user_logins;
               user_id                | device_type |            masked_ip             |                       masked_device_id                       | locale | app_version | create_date 
--------------------------------------+-------------+----------------------------------+--------------------------------------------------------------+--------+-------------+-------------
 424cdd21-063a-43a7-b91b-7ca1a833afae | android     | 199.172.111.0                    | 593-47-5928                                                  | RU     |         230 | 2023-02-02
 424cdd21-063a-43a7-b91b-7ca1a833afae | android     | 199.172.111.0                    | 593-47-5928                                                  | RU     |         230 | 2023-02-02
 c0173198-76a8-4e67-bfc2-74eaa3bbff57 | ios         | 241.6.88.0                       | 104-25-0070                                                  | PH     |          26 | 2023-02-02
 424cdd21-063a-43a7-b91b-7ca1a833afae | android     | 199.172.111.135                  | 593-47-5928                                                  | RU     |         230 | 2023-02-02
 c0173198-76a8-4e67-bfc2-74eaa3bbff57 | ios         | 241.6.88.0                       | 104-25-431                                                   | PH     |          26 | 2023-02-02
 424cdd21-063a-43a7-b91b-7ca1a833afae | android     | 199.172.111.0                    | 593-47-6537                                                  | RU     |         230 | 2023-02-02
 c0173198-76a8-4e67-bfc2-74eaa3bbff57 | ios         | 241.6.88.0                       | 104-25-198                                                   | PH     |          26 | 2023-02-02
 424cdd21-063a-43a7-b91b-7ca1a833afae | android     | 199.172.111.0                    | 593-47-6157                                                  | RU     |         230 | 2023-02-02
 c0173198-76a8-4e67-bfc2-74eaa3bbff57 | ios         | 241.6.88.0                       | 104-25-924                                                   | PH     |          26 | 2023-02-02
 66e0635b-ce36-4ec7-aa9e-8a8fca9b83d4 | ios         | 130.111.167.0                    | 127-42-1250                                                  | None   |         221 | 2023-02-02
(10 rows)
```

## Production Readiness 

#### -Deploying this application in production -
This can be deployed in production as a Continuous Integration and Continuous Deployment pipeline. GitHub can be used as the version control system to maintain each version of the application in case any rollback is required. On modifying the code a commit to the GitHub repository is made and the code pipeline pulls the latest change. It sends the updated code version to the CodeBuild cycle. 
CodeBuild then installs all the necessary dependencies with the latest code and runs the testing to perform validation checks. On successful installation and passed testing, the build artifacts are pushed to the S3 bucket. 
CodeDeploy will pull the latest build and deploy the build artifacts to a different S3 bucket now. Post this step, another CodeBuild will run.
Now the CodeBuild will run AWS CLI to take the latest build from the S3 bucket and update the Lambda function running this code with the latest code.

The lambda function is updated with the latest code and will now use the new code to run the application. 

##### Stages of the pipeline for production - 
- Fetching the Latest Code (Source)
- CodeBuild
- CodeDeploy
- Updating lambda by deploying the latest code on it.


#### -Other components to add to make this production ready - 
Other than the AWS CI/CD pipeline, some third-party testing tools can be added like checkmarx, Blackduck to ensure every version fo the code is not breaking when deployed in production. For provisioning of the resources in the production environment, tools like AWS Cloud Formation can be used. The credentials can be stored as a configuration in an S3 bucket in encrypted form and read via lambda when needed. 

#### -Scaling the application with growing dataset - 
Lambda automatically handles scaling the number of execution environments until you reach your account's concurrency limit. By default, Lambda provides your account with a total concurrency limit of 1,000 across all functions in a region. For storage, RDS also auto-scales with an increase in the load to the database. 

#### -Recovering PII later on - 
Using the hash function or Anonymization, the action cannot be reveresed to get the original data back. The masked column can then use this column to identify duplicates. One solution for unmasking can be, having a reference mapping between the masked IP and the original unmasked IP. This reference mapping can also be stored in the databse in a separate table that maps masked IP addresses back to the original IP addresses. This table can be reference internally when original IP is required and is a secure way to mask IPs because it cannot be unmasked using any method or decryption. To unmask the IP in the original table, a join can be used with the reference table.

#### -Assumptions - 

1. Running the cloud in a cloud service provider like AWS 
2. Hosting the application in a serverless architecture, hence, using AWS lambda
3. Growing dataset assumption - the number of commits to SQS increase which then increases the call on a lambda function 
4. Assuming the database is also in AWS, therefore suggesting AWS RDS.
5. The original unmasked values can be stored on the database so that an irreversible masking technique can be applied.
