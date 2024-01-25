from pandas import pd
from pymongo import MongoClient

#connect to mongodb
client = MongoClient('mongodb+srv://lucashlc:<password>@playerurls.8levfvn.mongodb.net/?retryWrites=true&w=majority')
database = client['web_scrape']
collection = database['playerURL']

#Load Excel Data and turn it into a pandas DataFrame object.
excel_file_path = 'Database.xlsx'
excel_file_df = pd.read_excel(excel_file_path, engine='openpyxl')

#Convert the Excel dataframe object into a list of dictionaries
data_to_append = excel_file_df.to_dict(oreit='records')

#Insert list of dictionaries into the collection
collection.insert_many(data_to_append)

#Close MongoDB Connection
client.close()

