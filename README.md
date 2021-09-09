<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Digikofy Front Back](#digikofy-front-back)
  - [Concernant ce projet](#concernant-ce-projet)
    - [Architecture](#architecture)
    - [Schema Base de Données NoSQL](#schema-base-de-donn%C3%A9es-nosql)
  - [Pour le lancer](#pour-le-lancer)
  - [API](#api)
    - [Routes disponibles](#routes-disponibles)
  - [Application React.js](#application-reactjs)
    - [Routes accessibles](#routes-accessibles)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Digikofy Front Back


## Concernant ce projet
<br/>
Ce projet a été réalisé à l'aide de React.js pour le front, Python à l'aide de la librairie FastAPI. Il est possible de se créer un compte ensuite de se
connecter pour avoir accès à une liste de cafés où l'on pourra accéder au detail de chacun.
<br/><br/>

### Architecture

<br/>

![Schema architecture projet digikofy front back](./assets/images/Architecture_Projet_Digikofy_Front_Back.png)

<br/>

### Schema Base de Données NoSQL
<br/>

![Schema Base de Données NoSQL](./assets/images/BDD_NoSQL.png)

<br/>

## Pour le lancer
<br/>
Pour lancer ce projet, ayant utilisé docker-compose pour faciliter le deploiement de cette application. Pour lancer le projet il suffit d'avoir installé docker, de pull le projet et taper la commande suivante à la racine où se trouve le docker-compose.yml :
<br/><br/>

```bash
    docker-compose up
```
<br/>

Il y a aussi la possibilité de récupérer les images séparément sur le docker hub avec les liens ci-dessous :

Back : https://hub.docker.com/repository/docker/kevintsi/digikofy-back

Front https://hub.docker.com/repository/docker/kevintsi/digikofy-front

Lors du lancement de l'API, vous aurez un appel à l'API toutes les 30 secondes pour vérifier la santé du conteneur.
<br/><br/>

```bash
digikofy-back-container | INFO:     127.0.0.1:36012 - "GET / HTTP/1.1" 200 OK
digikofy-back-container | INFO:     127.0.0.1:36016 - "GET / HTTP/1.1" 200 OK
digikofy-back-container | INFO:     127.0.0.1:36024 - "GET / HTTP/1.1" 200 OK
digikofy-back-container | INFO:     127.0.0.1:36034 - "GET / HTTP/1.1" 200 OK
digikofy-back-container | INFO:     127.0.0.1:36036 - "GET / HTTP/1.1" 200 OK
digikofy-back-container | INFO:     127.0.0.1:36042 - "GET / HTTP/1.1" 200 OK
digikofy-back-container | INFO:     127.0.0.1:36046 - "GET / HTTP/1.1" 200 OK

```
<br/>

Cependant cela peut être désactiver en commentant 
dans le fichier docker-compose.yml la ligne ci-dessous :
<br/><br/>

```yml
    healthcheck:
      test: curl --fail -s http://localhost:8000/ || exit 1
      interval: 30s
      timeout: 10s
      retries: 3
```
<br/>

Si tous les conteneurs se sont lancés sans aucun problèmes alors vous aurez les lignes suivantes :
<br/><br/>

```bash
  Recreating digikofy-front-container ... done
  Recreating digikofy-back-container  ... done
  Recreating digikofy-test-container  ... done
```
<br/>

## API
<br/>

### Routes disponibles 
<br/>

**index() :** 

***Route :*** "/"

***Méthode :*** GET

***Action :*** Retourne un JSON avec un message indiquant que le projet s'est lancé sans problème
<br/><br/>

-------------
<br/>

**get_coffees() :** 

***Route :*** "/coffees"

***Méthode :*** GET

***Action :*** Retourne tous les cafés
<br/><br/>

-------------
<br/>

**get_coffee() :** 

***Route :*** "/coffee/{id}"

***Méthode :*** GET

***Action :*** Retourne le café ayant l'id passé dans la route
<br/><br/>

-------------
<br/>

**login() :** 

***Route :*** "/login"

***Méthode :*** POST

***Body :***

***- email : string***

***- password : string***

***Action :*** Verifie si un utilisateur existe avec l'email et le mot de passe entré, s'il existe renvoie un token sinon renvoie un code 404
<br/><br/>

-------------
<br/>

**register() :** 

***Route :*** "/register"

***Méthode :*** POST

***Body :***

***- email : string***

***- password : string***

***Action :*** Verifie si un utilisateur avec cet email n'existe pas déjà si oui renvoie 409 si non, alors il ajoute l'utilisateur à la base de données
<br/><br/>

---------------
<br/>

**refresh_token() :** 

***Route :*** "/refreshToken"

***Méthode :*** POST

***Body :***

***- refresh_token : string***

***Action :*** Verifie si le refresh token ne se trouve pas dans la liste noire des refresh token, si oui alors il créer et renvoie un nouveau token à partir de ce refresh token
<br/><br/>

-----------------
<br/>

**revoke() :** 

***Route :*** "/revoke"

***Méthode :*** POST

***Body :***

***- refresh_token : string***

***Action :*** Ajoute le refresh token dans la liste noire

<br/>

---------------
<br/>

## Application React.js
<br/>

### Routes accessibles
<br/>

**Route :** "/register"

***Action :*** Affiche le formulaire d'inscription
<br/><br/>

---------------
<br/>

**Route :** "/login"

***Action :*** Affiche le formulaire de connexion
<br/><br/>

---------------
<br/>

**Route :** "/home"

***Action :*** Affiche la liste de cafés

**Route :** "/detail/{id}"

***Action :*** Affiche le détail du café ayant pour id celui passé dans la route



