from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import base64
import requests

#mongodb libraries
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd

#Create a Flask web application instance named app.
app = Flask(__name__, static_url_path='/static')

nba_refernce_main_url = "https://www.basketball-reference.com/"

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
collection2 = db["teams_url"]

# Game Scores
def score_scrape(url):
    # Scrape NBA games scores.
    scores_response = requests.get(url)
    scores_response.raise_for_status()
    
    soup = BeautifulSoup(scores_response.text, 'html.parser')
    
    # Data cleaning
    
    #remove all hyperlinks
    for a_tag in soup.find_all('a'):
        del a_tag['href']
        
    scores_div_name = 'game_summary'
    scores_class = soup.find_all('div', {'class': scores_div_name})
    
    
    games = {}
    if scores_class:
        for i in range(len(scores_class)):
            adder = str(i+1)
            games["game" + adder] = scores_class[i]
    return games
            

#Define a route for the root URL ('/'). When a user accesses the root URL, the index function is called. This function renders the index.html template.
@app.route('/')
def index():
    scores_content = score_scrape(nba_refernce_main_url)
    return render_template('index.html', scores_content=scores_content)

#Route for dropdown menu
@app.route('/get_options')
def get_options():
    search_value = request.args.get('url')
    print(f"Search Value: {search_value}")
    
    options = collection.distinct('Player', {'Player': {'$regex': search_value, '$options': 'i'}}) #used for regular expression searches on MongoDB, to parse for database fields that match the input element. 
    print(f"Options: {options}")
    
    return jsonify(options)

#Route for team options
@app.route('/get_team_options')
def get_team_options():
    search_value = request.args.get('team_url')
    print(f"Search Value: {search_value}")

    options = collection2.distinct('Team', {'Team': {'$regex': search_value, '$options': 'i'}})
    print(f"Options: {options}")
    
    return jsonify(options)


#Define a route for the /scrape URL with the HTTP method set to POST. This means that the function will be called when a POST request is made to the /scrape endpoint. The function retrieves the URL submitted in the form data.
@app.route('/scrape', methods=['POST'])
def scrape():
    
    searched_name = request.form['url'] #assigning a variable for the input of the form.
    search_document = collection.find_one({'Player': searched_name}) #query the database to find a document that has a Player key that is the same as the form input. Search variable becomes the
    print(search_document)
    #search collection and find a row where the Player key matches the serached name from the form.
    
    if search_document:
        desired_url =  search_document.get('URL', 'Default Value') #Returns Default Value if the URL key is not found.
    else:
        desired_url = 'No match found' #need to make a route for when a player is not found. will require new html.
    
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
                
        #player image:
        face_div_id = "media-item"
        face_div = soup.find('div', {'class': face_div_id})
        if face_div:
            img_tags = soup.find_all('img')
            player_img = (img_tags[1])
            player_image_url = player_img['src']
            print(player_image_url)
        
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
            'player_image': player_image_url,
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

# ---------------team scrape--------------
@app.route('/team_scrape', methods=['POST'])
def team_scrape():
    searched_name = request.form['team_url'] #assigning a variable for the input of the form.
    search_document = collection2.find_one({'Team': searched_name}) #query the database to find a document that has a Player key that is the same as the form input. Search variable becomes the
    print(search_document)

    if search_document:
        stats_url = search_document.get('Stats URL', 'Default Value') #Returns Default Value if the URL key is not found.
        print(stats_url)
        record_url = search_document.get('Record URL', 'Default Value')
    else:
        stats_url = 'No match found' #need to make a route for when a player is not found. will require new html.
        record_url = 'No match found'
    #search collection and find a row where the Player key matches the serached name from the form.
    
    try:
        # Team Stats Section
        response1 = requests.get(stats_url)
        response1.raise_for_status() #returns HTTP error object if error occured when tryig to get a response from the URL
        
        stats_soup = BeautifulSoup(response1.text, 'html.parser') #create soup object
        table_id = "all_team_and_opponent"
        stats_table = stats_soup.find_all('div', {'class': table_id})
        print(stats_table)
        
        # response for record url
        response2 = requests.get(record_url)
        response2.raise_for_status()

       
        record_soup = BeautifulSoup(response2.text, 'html.parser')

        title = stats_soup.title.string if stats_soup.title else 'No title found'
        #extracts the title of the url as a string, title becomes 'no title found' if the title cannot be found.


        h2_id = "team_and_opponent_sh"
        h2_elements = stats_soup.find('div', {'id': h2_id})
        if h2_elements:
            table_h2 = h2_elements.find_all('h2')
            if len(table_h2) >= 0:
                h2 = table_h2[0].get_text()
                print(h2)

        team_stats_table = stats_soup.find('table', id='team_and_opponent')

        # Check if the table is found
        # if team_stats_table:
        #     # Find the headers
        #     headers = [th.text for th in team_stats_table.find_all('th')]
            
        #     # Find data rows
        #     data_rows = team_stats_table.find_all('tr')[2:]  # Skip the first two rows as they contain headers and totals
            
        #     # Extract and print the data
        #     print("Team Stats:")
        #     print("\t".join(headers))
        #     for row in data_rows:
        #         cells = [cell.text.strip() for cell in row.find_all(['th', 'td'])]
        #         print("\t".join(cells))
        # else:
        #     print("Team stats table not found.")

        data = {
            'title': title,
        }
        
        return render_template('team_results.html', data=data)

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

    
    
if __name__ == '__main__':
    app.run(debug=True)
    