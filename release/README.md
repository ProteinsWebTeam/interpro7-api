`Release` folder
================

Contains code to import data from the DBs, transform it, and put it into the DW.

The models are the ones corresponding to the DBs the one for the DW are in the
`webfront` folder

To run the `populate_db` script that is in `management/commands/`, run
`./manage.py populate_db` with an optional number (defaults to 10) as the first
named parameter. This number corresponds to the number of every element
imported into the DW (useful for tests).
