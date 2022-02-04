from sqlite3 import DatabaseError
import unittest
from imdb_lib import httpIMDB
from unittest import TestCase
import pandas as pd

class TestClass(TestCase):
    
    def setUp(self) -> None:
        self.session = httpIMDB()
        self.df = pd.DataFrame()
        self.Id = 'tt0993846'

    def tearDown(self) -> None:
        self.assertIsNotNone(self.df)
        self.assertFalse(self.df.empty)
        self.assertFalse(self.df.isnull().values.any())
        self.assertEqual(sum(self.df.isna().sum().to_list()), 0)
        self.session.close_session()
        self.assertIsNotNone(self.Id)

    def test_getPopularTVShows(self):
        self.df = self.session.getPopularTVShows()

        self.assertEqual(len(self.df), 100)


    def test_getPopularMovies(self):
        self.df = self.session.getPopularMovies()

        self.assertEqual(len(self.df), 100)


    def test_getTopRatedTVShows(self):
        self.df = self.session.getTopRatedTVShows()

        self.assertEqual(len(self.df), 250)


    def test_getTopRatedMovies(self):
        self.df = self.session.getTopRatedMovies()

        self.assertEqual(len(self.df), 250)


    def test_getTitleDetails(self):
        self.df = self.session.getTitleDetails(self.Id)
        
        cols = self.df.columns.to_list()
        self.assertEqual(cols, 10)


    def test_searchTitle(self):
        self.df = self.session.searchTitle('Homem Aranha')


if __name__ == '__main__':
    unittest.main()