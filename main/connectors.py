from builtins import str
import pyodbc
import pandas as pd
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
	def get_column_with_dtype(self,table_name):
		if self.connection:
			table_name = table_name.split(".")[-1]
			query_string = query.get_column_with_dtype[self.db_driver].format(table_name)
			column_dtype = self.connection.execute(text(query_string))
			return column_dtype
	def incremental_load(self,target_file,table_name):
		if self.connection:
			print("this block executed-------->")
			target_table = target_file
			get_table_query_string = query.incremental_load['select_table_records'].format(table_name)
			primary_table_name = table_name.rsplit(".")[-1]
			schema_name = table_name.rsplit(".")[0]
			# print("table_name",schema_name)
			primary_column_query_string = query.get_primary_key[self.db_driver].format(schema_name, primary_table_name)
			primary_column_data = self.connection.execute(text(primary_column_query_string))
			primary_column = primary_column_data.fetchone()[0]
			source_table_data = self.connection.execute(text(get_table_query_string))
			source_table = pd.DataFrame(source_table_data.fetchall(), columns=source_table_data.keys())
			changes = source_table[~source_table.apply(tuple,1).isin(target_table.apply(tuple,1))]
			deletion = target_table[~target_table.apply(tuple,1).isin(source_table.apply(tuple,1))]
			if not deletion.empty:
				deletion = deletion[~deletion[primary_column].isin(source_table[primary_column])]
				target_table = target_table[~target_table[primary_column].isin(deletion[primary_column])]
			if not changes.empty:
				insert = changes[~changes[primary_column].isin(target_table[primary_column])]
				modified = changes[changes[primary_column].isin(target_table[primary_column])]
				if modified is not None:
					target_table = target_table[~target_table[primary_column].isin(modified[primary_column])]
    				# target_table = pd.concat([target_table, modified], ignore_index=True)
					target_table = pd.concat([target_table, modified], ignore_index=True)
					# return modified
				if insert is not None:
					target_table = pd.concat([target_table, insert], ignore_index=True)
				# 	combine = pd.concat([target_table,insert], ignore_index=True)
				# return modified
		return target_table
 
