######################################################################
########## import libraries
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
from pymongo.mongo_client import MongoClient
from splinter import Browser
# as a playground - we will try selenium as well
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
import pymongo
import time
#####################################################################
######### FUNCTIONS: Scrape
def scrape():
    """function scrapes mars.nasa and jpl.nasa web sites""" 
    #################################################################
    ##########getting titles and paragraph from latest MARS news
    print('started scraping')
    # using selenium setuping webdriver with chrome Headless options
    options=Options()
    options.headless=True
    # !!! WARNING chromdriver is in root repo directory... but u can give your own pass
    chrome_path='../chromedriver.exe'  # for example -  chrome_path='C://bin//chromedriver.exe'
    driver = webdriver.Chrome(chrome_path,options=options)

    # URL  of page for scraping
    url='https://mars.nasa.gov/news/'
    driver.get(url) 
    time.sleep(2)
    response = driver.page_source
    soup=bs(response,'lxml')
    # soup # debug print

    # close driver driver.close()
    driver.quit()
    # Declare output dictionary 
    scrape_dict={}

    ########## title search
    result=soup.body.find('div',class_='list_text').a
    news_title=result.text
    scrape_dict['news_title']=news_title
    # print(news_title) # debug rint

    ########## news paragraph search
    result=soup.body.find('div',class_='list_text').find('div',class_='article_teaser_body')
    news_p=result.text
    scrape_dict['news_p']=news_p
    # print(news_p) # debug rint

    #################################################################
    ########## getting Mars featured image url 
    # since JPL page has changed ( and homework is not updated for 2-3 years :) 
    #- we will get JPL Featured image instead
    # setting up exe-path to chrome and 
    #!!!!! change path to your machine
    executable_path={'executable_path':chrome_path} 
    # or use this code below
    #from webdriver_manager.chrome import ChromeDriverManager
    #executable_path = {'executable_path': ChromeDriverManager().install()}
    # estsblishing Browser instance headless
    with Browser('chrome', **executable_path,headless=True) as browser:
        #URL to visit
        url='https://www.jpl.nasa.gov/'
        browser.visit(url)
        # clicking on Galleries  in navbar 
        # try for big screen , except for small
        try:
            browser.find_by_xpath('//button[contains(..,"Galleries")]').click()
        except:
            # feature image does not show on small version of screen :
            browser.driver.set_window_size(1200, 800)
            time.sleep(1)
            browser.find_by_xpath('//button[contains(..,"Galleries")]').click()
        
        time.sleep(1)
        # clicking on featured image
        browser.find_by_xpath('//a[contains(..,"Featured Image")]').click()
        time.sleep(2)
        # copy link
        feature_image_link=browser.links.find_by_partial_href('images/jpeg')[0]['href']
        scrape_dict['feature_image']=feature_image_link
        # print(feature_image_link) # debug rint

    #################################################################
    ########## getting Mars facts with Pandas
    # establish url
    url='https://space-facts.com/mars/'
    tables = pd.read_html(url)
    # create HTML table 
    html_table = tables[0].to_html(header=False,index=False, justify='left',classes=['my_table','stripped'], border=0)
    scrape_dict['html_table']=html_table

    #################################################################
    ########## getting Mars hemispheres image urls
    # declare list for hemispheres image urls
    hem_list=[]
    # estsblishing Browser instance HEADLESS
    with Browser('chrome', **executable_path, headless=True) as browser:
        #URL to visit
        url='https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
        browser.visit(url)
        # get links for each hemisphere from search page
        links = browser.links.find_by_partial_text('Hemisphere')
        for i in range(0,len(links)):
            links[i].click()
            time.sleep(1)
            # getting image links from current page
            hem_image_link=browser.links.find_by_partial_href('enhanced')[0]['href']
            # getting title  from current page
            title=browser.find_by_xpath('//h2[@class="title"]')[0].text[:-len(' Enhanced')] #minus ' Enchanced'
            # recording list with dictionary
            hem_list.append({'title':title,'img_url':hem_image_link})
            browser.back()
            time.sleep(1)
            links = browser.links.find_by_partial_text('Hemisphere')
        # print(hem_list) # debug print
        scrape_dict['hem_list']=hem_list
    print('ended scarping')
    return scrape_dict

#####################################################################
######### FUNCTIONS: mars_insert
def mars_insert(page):
    """insert dictionary into mongodb"""
    # establishing connection to mongo instance
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    #client = pymongo.MongoClient('localhost', 27017)
    # Define database and collection
    db = client.mars_news_db
    #db=client['mars_news_db']
    collection = db.page_data
    #collection=db['page_data']
    record_count=collection.estimated_document_count()
    if record_count == 0:
        collection.insert_one(page)
        insertion='new data recorded'
    elif collection.find().sort('_id',-1).limit(1)[0]['news_title']!=page['news_title']:
        collection.insert_one(page)
        insertion='new data recorded'
    else:
        insertion='skip, no new record'
    client.close()
    return insertion

#####################################################################
######### FUNCTIONS: mars_search
def mars_search():
    """search and return latest record from mongodb"""
# establishing connection to mongo instance
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    #client = pymongo.MongoClient('localhost', 27017)
    # Define database and collection
    db = client.mars_news_db
    collection = db.page_data
    record_count=collection.estimated_document_count()
    if record_count == 0:
        dict=scrape()
        mars_insert(dict)
        
    record = collection.find().sort('_id',-1).limit(1)[0]
    client.close()
    return record  # change to just record 

# print(mars_search())
# print('serch is done')
# dict=scrape()
# print(mars_insert(dict))
# print(mars_search())