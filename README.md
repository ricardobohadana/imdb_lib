# IMDB_LIB Package
The main purpose of this package is to give acess to imdb data by scraping the website.

## Functionalities

### Import statemant
`httpIMDB` is the main class that you'll be using for now (_version 0.1_). It is responsible for all available data that can be retrieved.

```
from imdb_lib.session import httpIMDB

imdb = httpIMDB()
```
#
### `httpIMDB.getPopularTVShows()` and `httpIMDB.getPopularMovies()`
Scrape the top 100 most popular TV Shows/Movies according to the IMDB ranking

Returns a pandas dataframe with 100 rows and the following columns: `Id,title, poster, rating`

#
### `httpIMDB.getTopRatedTVShows()` and `httpIMDB.getTopRatedMovies()`
Scrape the top 100 most popular TV Shows/Movies according to the IMDB ranking

Returns a pandas dataframe with 250 rows and the following columns: `Id,title, poster, rating`

#
### `httpIMDB.getTitleDetails(id)`
Scrape the given title id for details


Returns a pandas dataframe with one row and the following columns: `title, poster, sinapse, rating, popularity, genres, types, top_cast, runtime, duration`

#
### `httpIMDB.searchTitle(title)`
As the name suggests, it is used to search for a title by its name

Requires 1 parameter, the title to be searched

Returns a pandas dataframe with the following columns: `Id and Title`
