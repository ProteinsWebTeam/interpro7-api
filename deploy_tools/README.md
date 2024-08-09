Provisioning a new site
=======================

## Required packages:

* Python 3
* Git
* pip

eg, on Ubuntu:

    sudo apt-get install git python3 python3-pip

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

    From now on all the command assume you are in the ```PROJECT/source``` directory.

3.  Start the virtual env in the assigned folder:

    ```bash
    python -m venv virtualenv
    ```

4.  Install requirements in the virtual environment

    ```bash
    ../virtualenv/bin/pip install -r requirements.txt
    ```

5.  Install requirements for development

        ```bash
        ../virtualenv/bin/pip install -r dev_requirements.txt
        ```

5.  Create a local configuration file in `config/interpro.local.yml`.
    In this file you can overwite any of the settings included in the read-only file `config/interpro.yml`.
    Below is an example of the local config that will run in debug mode using the test DB with SQLite, a local instance of elasticsearch without redis:
    ```yaml
    use_test_db: false
    debug: true
    allowed_host: ["localhost", "127.0.0.1"]
    searcher_path: "https://localhost:9200"
    searcher_index: "test"
    searcher_user: "elastic"
    searcher_password: "password"
    api_url: "http://localhost:8007/api/"
    static_url: "api/static_files/"
    searcher_test_path: "https://localhost:9200"
    searcher_test_password: "password"

    ```

    *   This configuration assumes a running instance of elasticsearch in port 9200. For details on how to install elasticsearch go
        [HERE](https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html)

6.  Migrate the database models (For SQLite)

    ```bash
     ../virtualenv/bin/python manage.py migrate
    ```

    If anything goes wrong check that the database directory exists

    ```bash
     ls ../database
    ```

7.  Collect the static files. Only necessary for server deployment.

    ```bash
    ../virtualenv/bin/python manage.py collectstatic --noinput
    ```

8.  Load the fixture data into the SQLite DB.
    ```bash
    ../virtualenv/bin/python manage.py loaddata webfront/tests/fixtures_*.json
    
9.  Install Elasticsearch and load index. Currently running version 8.12 with authentication by password

    e.g for OSX: brew install elasticsearch@8.12
    ```
    curl -XPUT 'localhost:9200/test?pretty' -H 'Content-Type: application/json' -d @config/elastic_mapping.json
    ```

10.  Run the tests. When running the tests, the API loads the fixtures in the existing elasticsearch instance, which is necessary to run the server with fixtures.
    ```
    ../virtualenv/bin/python manage.py test
    ```

11.  Start the server
    ```
    ../virtualenv/bin/python manage.py runserver 0.0.0.0:8000
    ```

12.  _[Optional]_ Install precommit, black and the pre-commit hook, to enable the formatting of files before each commit.
    ```
    ../virtualenv/bin/pip install pre-commit black
    ../virtualenv/bin/pre-commit install
    ```  
    *Note 1*:It is important to run the test in Python 3.8 because the VMs where the API runs use that version.



## Testing

The unit tests are located in `[project]/source/webfront/tests/`.

To run unit tests use 

```sh
../virtualenv/bin/python manage.py test webfront
```

The functional test are in `[project]/functional_tests` and are configured to Google Chrome (or Chromium), so you need to have it installed in your machine.

To run functional tests use

```sh
export BROWSER_TEST="chrome"

# Only required if ChromeDriver is not in your PATH
# or if its binary is not `chromedriver` (e.g. `chromium.chromedriver`)
export BROWSER_TEST_PATH="/path/to/chromedriver"

../virtualenv/bin/python manage.py test functional_tests
```

As a reference [HERE](https://docs.google.com/presentation/d/13_a6IbTq8KPGRH5AhsauEDJt4jEXNsT7DFdg1PNn4_I/edit?usp=sharing) is a graphic describing the fixtures.

All the test can be run at the same time:

```sh
../virtualenv/bin/python manage.py test
```

## Setting up real data (MySQL - elasticsearch)

For the next steps you need an installation of MySQL with a database compatible with the defined [model](https://github.com/ProteinsWebTeam/interpro7-api/blob/master/webfront/models/interpro_new.py).

1.  Remove the line `use_test_db: true` from the `config/interpro.local.yml` file.
    You could also set the value to false, but given that false is the default value, you can just remove it.

2.  Edit the same `config/interpro.local.yml` file, changing the `searcher_path` setting for one with the elastic search instance that corresponds with the data in MySQL.

3.  Copy the template mysql configuration file into `config/mysql.yml` and edit the file with your data.
    ```bash
    cp config/mysql.template.yml config/mysql.yml
    ```

3.  Start the server
    ```
    ../virtualenv/bin/python manage.py runserver 0.0.0.0:8000
    ```
