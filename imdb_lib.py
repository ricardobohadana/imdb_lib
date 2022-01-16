import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import quote

class IMDBHTTPSession():

    def __init__(self) -> None:
        self.SESSION = requests.Session()


    def __get_data__(self, url: str) -> pd.DataFrame:
        response = self.SESSION.get(url)
        html = BeautifulSoup(response.text, 'html.parser')

        posters = html.find_all('td', class_='posterColumn')

        posters_src = [rf"{poster.img['src']}" for poster in posters]
        
        titles = html.find_all('td', class_='titleColumn')
        titles_name = [rf'{title.a.text} {title.span.text}' for title in titles]
        ids = [title.a['href'].split('/')[2] for title in titles]

        ratings = html.find_all('td', class_='ratingColumn imdbRating')
        ratings_score = [rating.strong.text if rating.strong else 'None' for rating in ratings]

        out_dict = {
            'Id': ids,
            'Poster': posters_src,
            'Title': titles_name,
            'Rating': ratings_score
        }
        
        return pd.DataFrame(out_dict)
    
    
    def getPopularTVShows(self) -> pd.DataFrame:
        Url = 'https://www.imdb.com/chart/tvmeter'
        return self.__get_data__(Url)


    def getPopularMovies(self) -> pd.DataFrame:
        Url = 'https://www.imdb.com/chart/moviemeter/?ref_=nv_mv_mpm'
        return self.__get_data__(Url)


    def getTopRatedMovies(self) -> pd.DataFrame:
        Url = 'https://www.imdb.com/chart/top/?ref_=nv_mv_250'
        return self.__get_data__(Url)


    def getTopRatedTVShows(self) -> pd.DataFrame:
        Url = 'https://www.imdb.com/chart/toptv/?ref_=nv_tvv_250'
        return self.__get_data__(Url)


    def getTitleDetails(self, id: str) -> pd.DataFrame:
        url = 'https://www.imdb.com/title/' + quote(id)
        response = self.SESSION.get(url)

        html = BeautifulSoup(response.text, 'html.parser')

        # poster
        poster = html.find('img', class_ = 'ipc-image')['src']

        # sinapse
        try:
            sinapse = html.find('span', class_ = 'GenresAndPlot__TextContainerBreakpointXL-sc-cum89p-2').text 
        except AttributeError:
            sinapse = html.find('span', class_ = 'GenresAndPlot__TextContainerBreakpointXL-sc-cum89p-1').text

        # genres
        genre_div = html.find('div', class_='GenresAndPlot__GenresChipList-sc-cum89p-4')
        genres = [a_tag.span.text for a_tag in genre_div]

        # types
        ul_types = html.find('ul', class_='TitleBlockMetaData__MetaDataList-sc-12ein40-0')
        li_types = [li.a.text if li.find('a', recursive=False) else li.text for li in ul_types.children]

        # top_casts = html.find('div', class_='ipc-sub-grid ipc-sub-grid--page-span-2 ipc-sub-grid--wsraps-at-above-l ipc-shoveler__grid')

        default_avatar = 'https://www.kindpng.com/picc/m/421-4212275_transparent-default-avatar-png-avatar-img-png-download.png'

        top_casts = html.findAll('div', class_='StyledComponents__CastItemWrapper-sc-y9ygcu-7')

        top_cast = []
        for i, actor in enumerate(top_casts):
            new_actor = {}
            if i >= 5:
                break
            for idx, section in enumerate(actor):
                if idx == 0:
                    if not section.div.div.find('img'):
                        new_actor['avatar'] = default_avatar
                    else:
                        new_actor['avatar'] = section.div.div.img['src']
                elif idx == 1:
                    new_actor['name'] = section.a .text
                    new_actor['character'] = section.div.ul.li.a.span.text
            
            top_cast.append(new_actor)


        title = html.find('h1', class_='TitleHeader__TitleText-sc-1wu6n3d-0').text

        rating = html.find('span', class_='AggregateRatingButton__RatingScore-sc-1ll29m0-1').text

        popularity = html.find('div', class_='TrendingButton__TrendingScore-sc-bb3vt8-1').text


        output_dict = { 
            'title': title,
            'poster': poster,
            'sinapse':sinapse,
            'rating': str(rating),
            'popularity': str(popularity),
            # 'stars': stars,
            'genres': genres,
            'types': li_types,
            'top_cast': pd.DataFrame(top_cast)
        }

        return pd.DataFrame(output_dict)


    def searchTitle(self, title: str) -> pd.DataFrame:
        
        url = f'https://www.imdb.com/find?q={quote(title)}'
        response = self.SESSION.get(url)
        html = BeautifulSoup(response.text, 'html.parser')

        titles_tag = html.findAll('td', class_='result_text')
        titles = [t.a.text for t in titles_tag]
        ids = [t.a['href'].split('/')[2] for t in titles_tag]
        
        return pd.DataFrame({'Id': ids, 'Title': titles})
         

s = IMDBHTTPSession()
s.searchTitle('Homem Aranha')
print('done')