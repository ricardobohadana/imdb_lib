import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import quote

class httpIMDB():

    def __init__(self) -> None:
        self.SESSION = requests.Session()


    def close_session(self) -> None:
        self.SESSION.close()


    def __get_data__(self, url: str) -> pd.DataFrame:
        response = self.SESSION.get(url)
        html = BeautifulSoup(response.text, 'html.parser')

        posters = html.find_all('td', class_='posterColumn')

        posters_src = [rf"{poster.img['src']}" for poster in posters]
        
        titles = html.find_all('td', class_='titleColumn')
        titles_name = [rf'{title.a.get_text()} {title.span.get_text()}' for title in titles]
        ids = [title.a['href'].split('/')[2] for title in titles]

        ratings = html.find_all('td', class_='ratingColumn imdbRating')
        ratings_score = [rating.strong.get_text() if rating.strong else 'None' for rating in ratings]

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
            sinapse = html.find('span', class_ = 'GenresAndPlot__TextContainerBreakpointXL-sc-cum89p-2').get_text() 
        except AttributeError:
            sinapse = html.find('span', class_ = 'GenresAndPlot__TextContainerBreakpointXL-sc-cum89p-1').get_text()

        # genres
        genre_div = html.find('div', class_='GenresAndPlot__GenresChipList-sc-cum89p-4')
        genres = [a_tag.span.get_text() for a_tag in genre_div]

        # types
        ul_types = html.find('ul', class_='TitleBlockMetaData__MetaDataList-sc-12ein40-0')
        li_types = [li.a.get_text() if li.find('a', recursive=False) else li.get_text() for li in ul_types.children]

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
                    new_actor['name'] = section.a .get_text()
                    new_actor['character'] = section.div.ul.li.a.span.get_text()
            
            top_cast.append(new_actor)


        title = html.find('h1', class_='TitleHeader__TitleText-sc-1wu6n3d-0').get_text()

        rating = html.find('span', class_='AggregateRatingButton__RatingScore-sc-1ll29m0-1').get_text()

        popularity = html.find('div', class_='TrendingButton__TrendingScore-sc-bb3vt8-1').get_text()
        
        # while .text works, .get_text() is properly documented and so used as best practice
        runtime = html.find('li', {"data-testid":"title-techspec_runtime"})
        runtime_str = runtime.find('div').get_text()
        hours = re.search("(?P<hours>\d*) hours?", runtime.get_text())
        minutes = re.search("(?P<minutes>\d*) minutes?", runtime.get_text())
        
        # processing some times with ridiculous lengths, see https://www.imdb.com/title/tt3854496
        # this would be set to 59, except some films report a 60 minute runtime
        if int(minutes[1]) >60:
            # commas present an issue for ints, _ retained for readability
            if int(minutes[1])>999:
                max_minutes = minutes[1].replace(',', "_")
            else:
                max_minutes = minutes[1]
            sum_hours = int(max_minutes) // 60
            minutes = int(max_minutes) % 60
            hours = int(hours[1].replace(',', "_")) + sum_hours
        else:
            minutes = int(minutes[1])
            # couldn't find anything with over 720 hours of content, but in any case...
            hours = int(hours[1].replace(',', "_"))
        
        # duration is tuple of integers for the hours and minutes
        duration = (hours, minutes)
        

        output_dict = { 
            'title': title,
            'poster': poster,
            'sinapse':sinapse,
            'rating': str(rating),
            'popularity': str(popularity),
            'runtime' : runtime_str, # pulled directly from html string on page
            'duration' : duration, # calculated above
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
        titles = [t.a.get_text() for t in titles_tag]
        ids = [t.a['href'].split('/')[2] for t in titles_tag]
        
        return pd.DataFrame({'Id': ids, 'Title': titles})

