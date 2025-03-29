# Lulu-Teaches-MVP

## Get Start
The first step is to set up a virtual environment. If this is your first time working with this code, run the following command:  

```bash
python -m venv .venv
```  

This will create a virtual environment within your project directory.  

Next, you need to activate the virtual environment. Use the appropriate command based on your terminal:  

- **PowerShell:**  
  ```bash
  .venv/Scripts/Activate
  ```  

- **Command Prompt (CMD):**  
  ```bash
  .venv\Scripts\activate.bat
  ```  

Once activated, your virtual environment is ready to use.

## Installing Required Libraries  

After setting up your virtual environment, you need to install the necessary libraries for the project to run correctly. First, navigate to the project directory by running the following command:  

```bash
cd happy-kids
```  

This will take you to the *happy-kids* folder.  

Next, install all required dependencies by running:  

```bash
pip install -r requirements.txt
```  

This command will install all the necessary libraries for the project.

## Database
### Database Migrations in Docker Container
To start testing the implementation of the new data model, it is necessary to migrate to the local container. To do this, run the migration with the commands below:

First, make a local migrations
`python manage.py makemigrations`

`python manage.py migrate`

After that, initialize container migrations. To do that, it's necessary run the container service:
`docker compose up --build`

then:
`docker compose exec django-web python manage.py makemigrations`

`docker compose exec django-web python manage.py migrate`

### Database Migrations in Production
after carrying out the tests locally and all the constructions, it will be necessary to migrate the changes to google cloud SQL. Since the adjustments are only seen locally until then. 

To carry out this migration, some code adjustments must be made as indicated below:

Start by subscribing to the entire database layer in the settings.py file and add the field a new setting, as shown below:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '####', # real data
        'USER': '####', # real data
        'PASSWORD': '####', # real data
        'HOST': 'localhost',
        'PORT': '5050',
    }
}
```

Once the above changes have been made, the database must be started locally. To do this, run the command below:
`./cloud-sql-proxy --port 5050 lulu-mvp:europe-west3:db-lulu`

With the database running locally and the settings.py adjusted, we now just have to request the migration
`python manage.py migrate`

## Deploy
### Building a Docker Image For local testing
For local tests, after installing all the items listed above, run the command:
- `docker-compose up --build`

### Deploy new version of docker image on Google Cloud Platform
After testing locally as proposed above, deploy the new version following the steps below:
- `docker build -t gcr.io/lulu-mvp/lulu-teaches .`
- `docker push gcr.io/lulu-mvp/lulu-teaches`
- `gcloud run deploy lulu-teaches --image gcr.io/lulu-mvp/lulu-teaches --platform managed --region europe-west3 --vpc-connector lulu-vcp-network-serverle`

## References
- https://news.mit.edu/2023/large-language-models-in-context-learning-0207
- https://hbr.org/2022/11/how-generative-ai-is-changing-creative-work
- https://cloud.google.com/artifact-registry/docs?hl=pt-br
- https://cloud.google.com/build/docs?hl=pt-br
