
[![Build Status](https://travis-ci.org/ProteinsWebTeam/interpro7-api.svg?branch=master)](https://travis-ci.org/ProteinsWebTeam/interpro7-api)
[![Coverage Status](https://coveralls.io/repos/github/ProteinsWebTeam/interpro7-api/badge.svg?branch=master)](https://coveralls.io/github/ProteinsWebTeam/interpro7-api?branch=master)

## Interpro 7

This is the firs prototype to create an API for the new version of Interpro.

The architecture of the URL it is defined as a set of endpoints that can be freely combined to describe filters for each of them. The initial set of point is:

* entry
* protein
* proteome
* structure

The user can freely combine each of the endpoints. the only limitation is that a URL block describing an endpoint can only appears once in the URL. 

The google doc here contains more information about the design of this API: [Document](https://docs.google.com/document/d/1JkZAkGI6KjZdqwJFXYlTFPna82p68vom_CojYYaTAR0/edit?usp=sharing)

The procedure to install this project can be seen [HERE](deploy_tools/README.md).

This project follows the recommendations and guidelines presented in the book:
[Test-Driven Development with Python](http://chimera.labs.oreilly.com/books/1234000000754/index.html)
