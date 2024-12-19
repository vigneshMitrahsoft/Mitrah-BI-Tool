from builtins import str
# import pypyodbc as pyodbc
import pyodbc
import main.query as query
from sqlalchemy import create_engine,MetaData,inspect
from sqlalchemy.exc import SQLAlchemyError, InterfaceError
from sqlalchemy.sql import text
 
class connectors:
    
    def __init__(self, **kwargs):
        self.db_driver = kwargs.get('driver_name')
        try:
            params = f'{kwargs.get('user_name')}:{kwargs.get('password')}@{kwargs.get('server_name')}/{kwargs.get('database_name')}'
            if (self.db_driver == 'SQL Server'):
                self.connection_string = f'mssql+pyodbc://{params}?driver=ODBC+Driver+17+for+SQL+Server'
                self.query_string = query.get_tables['sql']
            elif (self.db_driver == 'MySQL'):
                self.connection_string =f'mysql+pymysql://{params}'
                self.query_string = query.get_tables['MySQL'].format(f"'{kwargs.get('database_name')}' ORDER BY TABLE_SCHEMA")
            elif (self.db_driver == 'PostgreSQL'):
                self.connection_string = f'postgresql+pg8000://{params}'
                self.query_string = query.get_tables['postgres']
            self.engine = create_engine(self.connection_string)
            self.connection = self.engine.connect()
        except  SQLAlchemyError as e:
            self.error = e
            print("error---->",type(self.error))
            self.connection = None

    def get_tables(self):
        if self.connection:
            try:
                self.query_result = self.connection.execute(text(self.query_string))
                all_table_name =[]
                for table in self.query_result:
                    concate_schema = table[0]+"."+table[1]
                    all_table_name.append(concate_schema)
                return all_table_name
            
            except SQLAlchemyError as e:
                print("Error occurred while fetching tables:", e)
                return {'error': str(e)}
        else:
            print("No connection established.")
            return {'error': str(self.error)}




    
        
   
