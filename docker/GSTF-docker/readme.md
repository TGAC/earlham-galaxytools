# GeneSeqToFamily Docker

The GeneSeqToFamily workflow is a comprehensive pipeline based on Ensembl Compara pipeline to find gene families. 

## Users and passwords

The Galaxy Admin User has the username admin@galaxy.org and the password admin. In order to use certain features of Galaxy, like e.g. workflows, one has to be logged in. Also the installation of additional tools requires a login.

The PostgreSQL username is galaxy, the password galaxy and the database name galaxy.

If you want to create new users, please make sure to use the /export/ volume. Otherwise your user will be removed after your docker session is finished.

## Starting docker

Starting the workflow is similar to start the generic Galaxy Docker image:

```
$ docker build -t <tag> . 
```

```
$ docker run -i -t -p 8080:80 <tag>
```

A detailed discussion of Docker's parameters is given in the [Docker manual](http://docs.docker.io/). It is really worth reading. Nevertheless, here is a quick rundown:

## Adding custom data

Docker configuration comes with test data, but if a user wants to start docker with custom data then modify the library_data.yml file as shown in example within. These data will be available as data libraries in Galaxy.

## Reference 

Anil S. Thanki, Nicola Soranzo, Wilfried Haerty, Robert P. Davey (2018) [GeneSeqToFamily: a Galaxy workflow to find gene families based on the Ensembl Compara GeneTrees pipeline](https://doi.org/10.1093/gigascience/giy005) *GigaScience* 7(3), giy005, doi: 10.1093/gigascience/giy005
