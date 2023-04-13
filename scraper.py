
#To get the url, and scrap the html page  
import requests
from bs4 import BeautifulSoup
#To save the reviews in a dataframe 
import pandas as pd

def meta_scrape():

    url = 'https://www.metacritic.com/browse/albums/score/metascore/90day/filtered'

    user_agent = {'User-agent': 'Mozilla/5.0'}
    response = requests.get(url, headers = user_agent)

    soup = BeautifulSoup(response.text, 'html.parser')

    album_df = pd.DataFrame(columns=['artist', 'album'])
    table_df = pd.DataFrame(columns=['pos','artist', 'album','score'])

    # for name in soup.find_all('div', class_='clamp-details'): 
    #     print(name.text)
    
    for name in soup.find_all("td", class_="clamp-summary-wrap"):        
        for score in name.find_all("div", class_="metascore_w large release positive"):
            score_text = score.text
        for pos in name.find_all("span", class_="title numbered"):     
            pos_text = pos.text.strip().replace('.','')
        for album in name.find('h3'):
            album_text = album.text
        for artist in name.find_all("div", class_="artist"):
            artist_text = artist.text.split('by')[1].strip()

        # result = {'pos':pos_text, 'artist':artist_text, 'album':album_text, 'score':score_text }
        result = {'pos':pos_text, 'artist':artist_text, 'album':album_text, 'score':score_text}
        
        table_df = table_df.append(result, ignore_index = True)
    
    table_df.to_csv('table.csv')

    return(table_df)

print(meta_scrape())
