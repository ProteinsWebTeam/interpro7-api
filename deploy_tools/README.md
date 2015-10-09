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
    └── SITENAME
         ├── database
         ├── source
         ├── static
         └── virtualenv
```

## Local Deployment

1.  Create directory structure in ~/sites
    
    ```
    mkdir -p PROJECT/database
    mkdir -p PROJECT/source
    mkdir -p PROJECT/static
    mkdir -p PROJECT/virtualenv
    ```
         
2.  Pull down source code into folder named source

    ```
    git clone https://github.com/ProteinsWebTeam/project-skeleton.git PROJECT/source 
    cd PROJECT/source
    ```

    From now on all the command assume you ar in the ```PROJECT/source``` directory.

3.  Start the virtual env in the assigned folder:
    
    ```
    virtualenv --python=python3 ../virtualenv
    ```
    
4.  Install requirements in the virtual environment

    ```
    ../virtualenv/bin/pip install -r requirements.txt
    ```
    
5.  Migrate the database models

    ```
     ../virtualenv/bin/python manage.py migrate
    ```
    
6.  Collect the static files. Only necessary for server deployment.

    ```
    ../virtualenv/bin/python manage.py collectstatic --noinput
    ```
    
7.  Edit the file  ```PROJECT/unifam/settings.py``` to include the credential of the PFAM database.
    
    **WARNING** If you are contributing to this project make sure you are not including a version of this file that 
    contains private information 

8.  Start the server
    ```
    ../virtualenv/bin/python manage.py runserver
    ```


## Testing

*   The unit tests are located in ```[project]/source/webfront/tests/tests.py```
    
    To run unit tests use ```../virtualenv/bin/python manage.py test webfront```

*   The functional test are in ```[project]/functional_tests/tests.py``` and they are configured to firefox, so you need 
    to have it installed in your machine
    
    To run functional tests use ```../virtualenv/bin/python manage.py test functional_tests```

All the test can be run at the same time:

```../virtualenv/bin/python manage.py test```