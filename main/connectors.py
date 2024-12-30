from builtins import str
import pyodbc
import main.query as query
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
 
class connectors:
    
    def __init__(self, **kwargs):
        self.db_driver = kwargs.get('driver_name')
        print("driver_name ---->",self.db_driver)
        try:
            params = f'{kwargs.get('user_name')}:{kwargs.get('password')}@{kwargs.get('server_name')}/{kwargs.get('database_name')}'
            if (self.db_driver == 'SQL Server'):
                self.connection_string = f'mssql+pyodbc://{params}?driver=ODBC+Driver+17+for+SQL+Server'
                self.query_string = query.string_query['sql']
            elif (self.db_driver == 'MySQL'):
                self.connection_string =f'mysql+pymysql://{params}'
                self.query_string = query.string_query['MySQL'].format(f"'{kwargs.get('database_name')}' ORDER BY TABLE_SCHEMA,TABLE_NAME")
            elif (self.db_driver == 'PostgreSQL'):
                self.connection_string = f'postgresql+pg8000://{params}'
                self.query_string = query.string_query['postgres']
            self.engine = create_engine(self.connection_string)
            self.connection = self.engine.connect()
        except  SQLAlchemyError as e:
            self.error = e
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
                return {'error': str(e)}
        else:
            return {'error': str(self.error)}
    
    def get_selected_tables(self,table):
        if self.connection:
            query_string = f"select * from {table}"
            selected_table = self.connection.execute(text(query_string))
            return selected_table     
        "oUw7hMVhht6hm7eFr4DtTztoyzfK4TJCGXQVegSKBeHpi1nT9aB6BkhaphstEJnKHOkaq9u8qt3rUo5IajNYm8gFX4KAGsKcWYYvAgAsXd88P7eh7x67D3zc+aLjT89DRhV/xYi98jKBkYJUFUP2XDcnwF7H0wXm39clQro6oTkO8vCAmfDz8WCCPf2kKIZexCalGGTtVvwobVnAacWMNA=="





    
        
   
