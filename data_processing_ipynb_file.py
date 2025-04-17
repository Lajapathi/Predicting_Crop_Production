### LIB 
# ! pip install pandas
# ! pip install sqlalchemy
# ! pip install psycopg2-binary
import pandas as pd
import sqlalchemy

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float , Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

### CSV to DATA FRAME
df=pd.read_csv('/Users/apple/Documents/Guvi/Projects/Predicting Crop Production/FAOSTAT_data - FAOSTAT_data_en_12-29-2024.csv')

df.drop(columns=['Item Code (CPC)','Note'], inplace=True)


## Data correction 
### Flag Description and Flag

# These values refered from data

df.loc[(df['Flag'] == 'A') & (df['Flag Description'].isna()), 'Flag Description'] = 'Official figure'
df.loc[(df['Flag'] == 'I') & (df['Flag Description'].isna()), 'Flag Description'] = 'Imputed value'
df.loc[(df['Flag'] == 'E') & (df['Flag Description'].isna()), 'Flag Description'] = 'Estimated value'
df.loc[(df['Flag'] == 'M') & (df['Flag Description'].isna()), 'Flag Description'] = 'Original'
df.loc[(df['Flag'] == 'X') & (df['Flag Description'].isna()), 'Flag Description'] = 'Missing value (data cannot exist, not applicable)'

df.loc[(df['Flag Description'] == 'Official figure') & (df['Flag'].isna()), 'Flag'] = 'A'
df.loc[(df['Flag Description'] == 'Imputed value') & (df['Flag'].isna()), 'Flag'] = 'I'
df.loc[(df['Flag Description'] == 'Estimated value') & (df['Flag'].isna()), 'Flag'] = 'E'
df.loc[(df['Flag Description'] == 'Original') & (df['Flag'].isna()), 'Flag'] = 'M'
df.loc[(df['Flag Description'] == 'Missing value (data cannot exist, not applicable)') & (df['Flag'].isna()), 'Flag'] = 'X'


df.loc[df['Flag'].isna() & df['Flag Description'].isna(), ['Flag', 'Flag Description']] = ['M', 'Missing value (data cannot exist, not applicable)']

### Value and Unit

df['Value'] = df['Value'].fillna(df['Value'].median())
df.loc[df['Unit'].isna(), 'Unit'] = 'No'

### Seperate crop type

import re
def split_items(row):
    if pd.isna(row['Item']):
        return [None]
    # Split on commas or 'and', handling extra whitespace
    items = re.split(r',\s*|\s+and\s+', row['Item'])
    return [i.strip() for i in items if i.strip()]

# Create a new column with split item lists
df['Item List'] = df.apply(split_items, axis=1)

# Explode the DataFrame to get one item per row
df = df.explode('Item List')

# Replace original 'Item' column with split version
df['Item'] = df['Item List']
df.drop(columns=['Item List'], inplace=True)

# Reset index
df.reset_index(drop=True, inplace=True)

## Database actions
### Connection

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
### Creating table 'crop_production_prime'
Base=declarative_base()

class forest(Base):
  __tablename__='crop_production_prime'

  Sno=Column(Integer,primary_key=True,autoincrement=True)
  for column , dtype in df.dtypes.items():
    if dtype=='object':
      column_type=String
    elif dtype=='bool':
      column_type=Boolean
    elif dtype=='datetime64[ns]':
      column_type=DateTime
    elif dtype=='float64':
      column_type=Float
    elif dtype=='int32':
      column_type=Integer
    elif dtype=='int64':
      column_type=Integer
    else:
      column_type=String

    locals()[column]=Column(column,column_type)

  def __repr__(self):
        # Create a dynamic string that includes all column names and their values
        columns = [f"{col}={getattr(self, col)}" for col in self.__table__.columns.keys()]
        return f"<User({', '.join(columns)})>"

Base.metadata.create_all(engine)
Session=sessionmaker(bind=engine)
session=Session()
session.commit()
### Table insertion
df.columns = df.columns.str.lower()
df.to_sql('crop_production_prime',engine,if_exists='replace',index=False)