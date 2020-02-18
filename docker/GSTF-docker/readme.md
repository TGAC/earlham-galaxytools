# GeneSeqToFamily Docker

The GeneSeqToFamily workflow is a comprehensive pipeline based on Ensembl Compara pipeline to find gene families. 

## Users and passwords

The Galaxy Admin User has username `admin@galaxy.org` and password `admin`. In order to use certain features of Galaxy, for example workflows, one has to be logged in. Also the installation of additional tools requires a login.

The PostgreSQL username is `galaxy`, the password `galaxy` and the database name `galaxy`.

For more information please have a look at: https://github.com/bgruening/docker-galaxy-stable/blob/master/README.md 

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

Docker configuration comes with test data, but if you want to pre-load custom data, then modify the `library_data.yml` file as shown in the example within. These data will be available as data libraries in Galaxy.

## Reference 

Anil S. Thanki, Nicola Soranzo, Wilfried Haerty, Robert P. Davey (2018) [GeneSeqToFamily: a Galaxy workflow to find gene families based on the Ensembl Compara GeneTrees pipeline](https://doi.org/10.1093/gigascience/giy005) *GigaScience* 7(3), giy005, doi: 10.1093/gigascience/giy005
