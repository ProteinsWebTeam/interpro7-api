Provisioning a new site
=======================

## Required packages:

* Python 3
* Git
* pip
* virtualenv

eg, on Ubuntu:

    sudo apt-get install git python3 python3-pip
    sudo pip3 install virtualenv

## Folder structure:
Assume we have a user account at /home/username

```
/home/username
└── sites
    └── PROJECT
         ├── database
         ├── source
         ├── static_files
         └── virtualenv
```

## Local Deployment

1.  Create directory structure in ~/sites

    ```bash
    mkdir -p PROJECT/database
    mkdir -p PROJECT/source
    mkdir -p PROJECT/static_files
    mkdir -p PROJECT/virtualenv
    ```

2.  Pull down source code into folder named source

    ```bash
    git clone https://github.com/ProteinsWebTeam/interpro7-api.git PROJECT/source
    cd PROJECT/source
    ```

    From now on all the command assume you ar in the ```PROJECT/source``` directory.

3.  Start the virtual env in the assigned folder:

    ```bash
    virtualenv --python=python3 ../virtualenv
    ```

4.  Install requirements in the virtual environment

    ```bash
    ../virtualenv/bin/pip install -r requirements.txt
    ```
    
    *  [Optional] Install requirements for development

        ```bash
        ../virtualenv/bin/pip install -r dev_requirements.txt
        ```

5.  Create a local configuration file in `config/interpro.local.yml`. 
    In this fil you can overwite any of the settings included in the read-only file `config/interpro.yml`.
    Below is an example of the local config that will run in debug mode using the test DB with SQLite, a local instance of elasticsearch without redis:
    ```yaml
    use_test_db: true
    debug: true
    allowed_host: []
    searcher_path: "http://localhost:9200/current/relationship"
    searcher_test_path: "http://localhost:9200/test/relationship"
    api_url: "http://localhost:8007/api/"
    enable_caching: false
    enable_cache_write: false

    ```
    
    *   This configuration assumes a running instance of elasticsearch in port 9200. For deatils on how to install elasticsearch go
        [HERE](https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html)
 
6.  Migrate the database models (For SQLite)

    ```bash
     ../virtualenv/bin/python manage.py migrate
    ```

7.  Collect the static files. Only necessary for server deployment.

    ```bash
    ../virtualenv/bin/python manage.py collectstatic --noinput
    ```

8.  Load the fixture data into the SQLite DB.
    ```bash
    ../virtualenv/bin/python manage.py loaddata webfront/tests/fixtures_*.json
    ```

9.  Run the tests. When running the tests, the API loads the fixtures in the existing elasticsearch instance, which is necessary to run the server with fixtures.
    ```
    ../virtualenv/bin/python manage.py test
    ```

10.  Start the server
    ```
    ../virtualenv/bin/python manage.py runserver 0.0.0.0:8000
    ```


## Testing

*   The unit tests are located in ```[project]/source/webfront/tests/tests.py```

    To run unit tests use ```../virtualenv/bin/python manage.py test webfront```

*   The functional test are in ```[project]/functional_tests/tests.py``` and they are configured to firefox, so you need
    to have it installed in your machine

    To run functional tests use ```../virtualenv/bin/python manage.py test functional_tests```

*   As a reference [HERE](https://docs.google.com/presentation/d/13_a6IbTq8KPGRH5AhsauEDJt4jEXNsT7DFdg1PNn4_I/edit?usp=sharing) is a graphic describing the fixtures.

All the test can be run at the same time:

```../virtualenv/bin/python manage.py test```

## Setting up real data (MySQL - elasticsearch)

For the next steps you need an installation of MySQL with a database compatible with the defined [model](https://github.com/ProteinsWebTeam/interpro7-api/blob/master/webfront/models/interpro_new.py). 

1.  Remove the line `use_test_db: true` from the `config/interpro.local.yml` file. 
    You could also set the value to true, but given that true is the default value, you can just remove it.

2.  Edit the same `config/interpro.local.yml` file, changing the `searcher_path` setting for one with the elastic search instance that correspond with the data in MySQL.

3.  Copy the template mysql configuration file into `config/mysql.yml` and edit the file with your data.
    ```bash
    cp config/mysql.template.yml config/mysql.yml 
    ```
    
3.  Start the server
    ```
    ../virtualenv/bin/python manage.py runserver 0.0.0.0:8000
    ```
