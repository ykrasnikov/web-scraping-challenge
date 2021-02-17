#####################################################################
########## import libraries
import pymongo
from flask import Flask
from scrape_mars import scrape, mars_insert,mars_search

app=Flask(__name__)

@app.route('/')
def main():
    app.logger.info('START DB SEARCH')
    dict=mars_search()
    app.logger.info('END DB SEARCH')

    return dict


@app.route('/scrape')
def reload():
    app.logger.info('START SCRAPE')
    dict=scrape()
    app.logger.info('STOP SCRAPE')
    app.logger.info('START DB INSERT')
    result=mars_insert(dict)
    app.logger.info('STOP DB INSERT')

    return'hello word %s!' % result






if __name__=='__main__':
    app.run(debug=True)
