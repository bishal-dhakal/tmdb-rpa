from robocorp.tasks import task
import pandas as pd
import time
import traceback
import sqlite3
from RPA.Browser.Selenium import Selenium
from robot.libraries.BuiltIn import BuiltIn

movies = []

browser = Selenium()

def read_xcl():
    df = pd.read_excel("../movies.xlsx")
    movie = df["Movie"]

    for m in movie:
        movies.append(m)
    
def mainWork():
    try:
        read_xcl()

        conn = sqlite3.connect('imdb.db')
        cur = conn.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY,
        movie_name TEXT,
        overview TEXT,
        tagline TEXT,
        user_score TEXT,
        genres TEXT,
        review_1 TEXT,
        review_2 TEXT,
        review_3 TEXT,
        review_4 TEXT,
        review_5 TEXT,
        status TEXT
        )""")
        browser.open_available_browser("https://www.themoviedb.org/", maximized=True)

        searchbox_path = '//a[@class="search"]'
        next_search_path = '//input[@id="search_v4"]'
        movie_path = '//div[@class="title"]//a'
        review_el = '//section[@class="review"]//p[@class="new_button"]/a'
        reviews_path ='//div[@class="card"]//p[1]'

        for movie in movies:
            BuiltIn().log_to_console(f"searching for {movie}")
            browser.auto_close = False

            #search movie
            browser.click_element_when_visible(searchbox_path)
            browser.wait_until_element_is_visible(next_search_path)
            browser.input_text(next_search_path,movie)

            browser.press_keys(None, 'RETURN')

            flim_el = browser.find_elements(movie_path)
            # BuiltIn().log_to_console(len(flim_el))

            latest_date = 0
            date_el = browser.find_elements('//div[@class="title"]/span')
            
            for i , flims in enumerate(flim_el):

                title = browser.get_text(flims) 

                if title == movie:
                    try:
                        date = browser.get_text(date_el[i])
                        date = int(date[-4:])
                    except:
                        continue
                    
                    if date > latest_date:
                        latest_date = date
                        latest_flim_el = flims

            try:
                if(latest_date):
                    link = browser.get_element_attribute(latest_flim_el,'href')
                    browser.go_to(link)
                    try:
                        ratings = browser.get_element_attribute('//div[@class="user_score_chart"]','data-percent')
                    except:
                        ratings = "Not Found"

                    try:
                        storyline = browser.get_text('//div[@class="overview"]')
                    except:
                        storyline = "Not Found"

                    try:
                        tagline = browser.get_text('//h3[@class="tagline"]')
                    except:
                        tagline = "Not Found"
                    
                    try:
                        genres = browser.get_text('//span[@class="genres"]')
                    except:
                        genres = "Not Found"

                    # review
                    try:
                        reviews = []
                        link = browser.get_element_attribute(review_el,'href')
                        browser.go_to(link)
                        reviews_el = browser.find_elements(reviews_path)

                        for reviwe_el in reviews_el:
                            review = browser.get_text(reviwe_el)
                            reviews.append(review)

                        BuiltIn().log_to_console('chalirachha at try')
                    except:
                        review=[]
                        if(len(reviews) < 5 ):
                            for i in range(5-len(reviews)):
                                reviews.append("Not Found")
                        
                        BuiltIn().log_to_console('chalirachha at except')

                    status = "Success"

                    
                    cur.execute("""INSERT INTO movies (movie_name, overview, tagline, user_score,genres, review_1, review_2, review_3, review_4, review_5,status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (movie, storyline,tagline ,ratings, genres,  reviews[0], reviews[1], reviews[2], reviews[3], reviews[4], status))
                else:
                    status = 'Not Found'
                    cur.execute("""INSERT INTO movies (movie_name, overview, tagline, user_score,genres, review_1, review_2, review_3, review_4, review_5,status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (movie, 'Not Found','Not Found' ,'Not Found', 'Not Found', 'Not Found', 'Not Found', 'Not Found', 'Not Found', 'Not Found', status))
                
                conn.commit()
            except:
                pass

        browser.close_all_browsers()
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        
@task
def minimal_task():
    mainWork()
