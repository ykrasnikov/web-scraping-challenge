#####################################################################
########## import libraries
import pymongo
from flask import Flask, render_template
from functions_scrape_mars import scrape, mars_insert,mars_search

app=Flask(__name__)

@app.route('/')
def main():
    app.logger.info('START DB SEARCH')
    dict=mars_search()
    app.logger.info('END DB SEARCH')
    app.logger.info(dict)

    return render_template('home.html',dict=dict)


@app.route('/scrape')
def reload():
    app.logger.info('START SCRAPE')
    dict=scrape()
    app.logger.info('STOP SCRAPE')
    app.logger.info('START DB INSERT')
    result=mars_insert(dict)
    app.logger.info(result)
    app.logger.info('STOP DB INSERT')

    return render_template('home.html',dict=dict)






if __name__=='__main__':
    app.run(debug=True)
