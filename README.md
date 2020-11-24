
[![Unit and Funtional Testing](https://github.com/ProteinsWebTeam/interpro7-api/workflows/Unit%20and%20Funtional%20Testing/badge.svg)](https://github.com/ProteinsWebTeam/interpro7-api/actions?query=workflow%3A%22Unit+and+Funtional+Testing%22)
[![Coverage Status](https://coveralls.io/repos/github/ProteinsWebTeam/interpro7-api/badge.svg?branch=master)](https://coveralls.io/github/ProteinsWebTeam/interpro7-api?branch=master)
[![GitHub license](https://img.shields.io/badge/license-apache-blue.svg)](https://github.com/ProteinsWebTeam/interpro7-api/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

![Logo InterPro7](https://raw.githubusercontent.com/ProteinsWebTeam/interpro7-api/master/webfront/static/logo_178x178.png  "Logo InterPro7")

## Interpro 7 API

InterPro provides functional analysis of proteins by classifying them into families and predicting domains and important sites. 

This is the repository for the source code running the InterPro Rest API, which is currently available at [https://www.ebi.ac.uk/interpro/api/].

This API provides the data that the new InterPro website uses. You can explore the website at [www.ebi.ac.uk/interpro].

The repository for the InterPro Website can be found at [https://github.com/ProteinsWebTeam/interpro7-client].


#### API URL Design

The InterPro API can be accessed by any of its 6 endpoints: 

* entry
* protein
* structure
* set
* taxonomy
* proteome



if the URL only contains the name of the endpoint (e.g. `/structure`), the API returns an overview object with counters of the chosen entity grouped by its databases. 

For each endpoint the user can specify a database (e.g. `/entry/pfam`), and the API will return a list of the instance in such database.

Similarly, the user can include an accession of an entity in that endpoint (e.g. `/protein/uniprot/P99999`), which will return an object with detailed metadata of such entity. 

The user can freely combine the endpoint blocks (e.g. `/entry/interpro/ipr000001/protein/reviewed`). The only limitation is that a block describing an endpoint can only appears once in the URL. 

The google doc here contains more information about the URL design of this API: [Document](https://docs.google.com/document/d/1JkZAkGI6KjZdqwJFXYlTFPna82p68vom_CojYYaTAR0/edit?usp=sharing)


#### Dependencies

InterPro7 API runs on [Python3](https://docs.python.org/3/) and uses [Django](https://www.djangoproject.com/) as its web framework, 
together with the [Django REST framework](http://www.django-rest-framework.org/) to implement the REST API logic.

Another set of dependencies in the codebase are related to data access. Our data storage has 3 sources, a MySQL database for the metadata of all our entities, an elasticsearch instance for the links between them, and, optionally, redis to cache responses of often used requests.
The python clients used to communicate with the sources are: mysqlclient, redis and django-redis. For elastic search we use regular http transactions, and therefore no client is required.

The specific versions of these dependencies can be found in the file [requirements.txt](https://github.com/ProteinsWebTeam/interpro7-api/blob/master/requirements.txt). Other minor dependencies are also included in the file.

An optional set of dependencies, not required to run the API, but useful for development purposes can be found in [dev_requirements.txt](https://github.com/ProteinsWebTeam/interpro7-api/blob/master/dev_requirements.txt).


#### Local Installation

The procedure to install this project can be seen [HERE](deploy_tools/README.md).

#### Developers Documentation

Some details about decisions, compromises an d techniques used throughout the project can be found [HERE](./webfront/README.md)

---
This project followed some of the recommendations and guidelines presented in the book:
[Test-Driven Development with Python](http://www.obeythetestinggoat.com/)
