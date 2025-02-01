# Tapahtumakalenteri

## Sovelluksen nykyiset toiminnot

* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan tapahtumia.
* Käyttäjä pystyy lisäämään kuvan tapahtumaan.
* Käyttäjä pystyy lisäämään hinnan tapahtumaan.
* Käyttäjä pystyy valitsemaan tapahtuman kategorian.
* Käyttäjä näkee sovellukseen lisätyt tapahtumat.
* Käyttäjä pystyy etsimään tapahtumia hakusanalla.

## Sovelluksen puuttuvat toiminnot

* Käyttäjä pystyy ilmoittautumaan tapahtumaan ja lähettää kysymyksiä järjestäjälle.
* Käyttäja pystyy näkemään omat ilmoittautumiset.
* Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät tapahtumat.
  
## Sovelluksen suorittaminen

Asenna `flask`-kirjasto:

```
$ pip install flask
```

Luo tietokannan taulut:

```
$ sqlite3 database.db < schema.sql
```

Suorita sovellus:

```
$ flask run
```
