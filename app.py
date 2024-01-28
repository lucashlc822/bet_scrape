from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests

#mongodb libraries
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd

#Create a Flask web application instance named app.
app = Flask(__name__)


#Initalize MongoDB
uri = "mongodb+srv://lucashlc:NBAurl12345@nba.kewvdct.mongodb.net/?retryWrites=true&w=majority" 
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["players"]
collection = db["URL"]

#Define a route for the root URL ('/'). When a user accesses the root URL, the index function is called. This function renders the index.html template.
@app.route('/')
def index():
    return render_template('index.html')

#Define a route for the /scrape URL with the HTTP method set to POST. This means that the function will be called when a POST request is made to the /scrape endpoint. The function retrieves the URL submitted in the form data.
@app.route('/scrape', methods=['POST'])
def scrape():
    
    searched_name = request.form['url']
    search = collection.find_one({'Player': searched_name})
    print(search)
    #search collection and find a row where the Player key matches the serached name from the form.
    
    if search:
        desired_url =  search.get('URL', 'Default Value') #Returns Default Value if the URL key is not found.
    else:
        desired_url = 'No match found'
    
    #Use the requests.get method to make an HTTP GET request to the specified URL. The try block handles the potential exceptions that may occur during the request. response.raise_for_status() checks if the request was successful, and if not, it raises an exception.
    try:
        response = requests.get(desired_url)
        response.raise_for_status() #returns HTTP error object if error occured when tryig to get a response from the URL
        
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else 'No title found'
        #extracts the title of the url as a string, title becomes 'no title found' if the title cannot be found.
        
        #player name:
        name_div_id = "meta"
        name_div = soup.find('div', {'id': name_div_id})
        player_name = "No Name"
        
        if name_div:
            name_h1 = soup.find_all('h1')
            print(name_h1)
            if len(name_h1) >= 0:
                player_name = name_h1[0].get_text()
        
        
        #player stats section:
        stats_div_class_1 = "p1"
        stats_div = soup.find('div', {'class': stats_div_class_1})
        
        if stats_div:
            stats_paragraphs = stats_div.find_all('p')
            games_played = stats_paragraphs[0].get_text() if len(stats_paragraphs) > 0 else "No Games Played Found"
            ppg = stats_paragraphs[2].get_text() if len(stats_paragraphs) > 2 else "No PPG Found"
            rebounds = stats_paragraphs[4].get_text() if len(stats_paragraphs) > 4 else "No Rebounds Found"
            assists = stats_paragraphs[6].get_text() if len(stats_paragraphs) > 6 else "No Assists Found"
            
            data = {
            'title': title,
            'Name': player_name,
            'GP': games_played,
            'PPG': ppg,
            'Rebounds': rebounds,
            'Assists': assists,
            }
        
            return render_template('results.html', data=data)
        
        else:
            stats_div = f'No Div found with class "{stats_div_class_1}" found'
            print(stats_div)
            return render_template('failed.html', stats_div = stats_div)
            
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    
if __name__ == '__main__':
    app.run(debug=True)
    