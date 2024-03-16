from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd

uri = "mongodb+srv://lucashlc:NBAurl12345@nba.kewvdct.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["players"] #select the players database
collection = db["teams_url"] #select the URL collection (table/document)

excel_file_path = 'Teams.xlsx'

df = pd.read_excel(excel_file_path, engine='openpyxl') #convert the excel file into a pandas dataframe object

append_data = df.to_dict(orient='records') #convert the pandas dataframe object into a dictionary.

collection.insert_many(append_data)  #append dicionary into the collection document/table on MongoDB
