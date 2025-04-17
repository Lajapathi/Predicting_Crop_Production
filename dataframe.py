import sqlalchemy 
from sqlalchemy import create_engine
import pandas as pd 

#Database credential
host='localhost'
port='5432'
username='postgres'
password='laja1103'
database='Crop_Production'

# connection string
connection_string=f"postgresql://{username}:{password}@{host}:{port}/{database}"

#creating engine
engine=create_engine(connection_string)


query='''select distinct * from  crop_production_prime'''
def crop_production_data():
    crop_production_df=pd.read_sql_query(query,engine)
    return crop_production_df

df=crop_production_data()
df.to_csv('crop_production_prime.csv', index=False)
