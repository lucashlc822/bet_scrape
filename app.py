from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests

#Create a Flask web application instance named app.
app = Flask(__name__) 

#Define a route for the root URL ('/'). When a user accesses the root URL, the index function is called. This function renders the index.html template.
@app.route('/')
def index():
    return render_template('index.html')

#Define a route for the /scrape URL with the HTTP method set to POST. This means that the function will be called when a POST request is made to the /scrape endpoint. The function retrieves the URL submitted in the form data.
@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form['url']
    
    #Use the requests.get method to make an HTTP GET request to the specified URL. The try block handles the potential exceptions that may occur during the request. response.raise_for_status() checks if the request was successful, and if not, it raises an exception.
    try:
        response = requests.get(url)
        response.raise_for_status() #returns HTTP error object if error occured when tryig to get a response from the URL
        
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else 'No title found'
        #extracts the title of the url as a string, title becomes 'no title found' if the title cannot be found.

        #games played, parsing all paragraphs, then finding the text of the paragraph desired.
        paragraphs = soup.find_all('p')
        print("pargraphs array", paragraphs)
        games_played_content = paragraphs[13].get_text() if len(paragraphs) > 13 else "No Info on Games Played"

        #par = [p.get_text() for p in soup.find_all('p')]
        # extract the text values of each paragraph on the website and append them into a list.

        data = {
            'title': title,
            'games_played': games_played_content,
        }

        return render_template('results.html', data=data)
    
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    
if __name__ == '__main__':
    app.run(debug=True)