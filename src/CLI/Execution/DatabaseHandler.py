import mysql.connector
import json
from mysql.connector import Error

class DatabaseHandler:
    def __init__(self):
        pass
    
    def connection(self):
        print("Establising connection to the Database....")
        try:
            connect = mysql.connector.connect(
                host = ' 192.168.56.1',
                user = 'lmillar',
                password = 'Grannyanna1',
                database = 'unified_framework_tool'
            )
            print("Connection to the Database successfully established!")
            return connect
        except Error as e:
            print(f"Connection to database failed: {e}")
            return None
    
    def closeConnection(self, connect):
        print("Exiting Database....")
        return connect.close()

    def insert_data(self, connect, table_name, field_names, data_values):
        if connect is None:
            return
        cursor = connect.cursor()
        try:
            fields = ', '.join(field_names)
            placeholders = ', '.join(['%s'] * len(data_values))
            insert_query = f'INSERT INTO {table_name} ({fields}) VALUES ({placeholders})'
            cursor.execute(insert_query, data_values)
            connect.commit()
            last_insert_id = cursor.lastrowid
            return last_insert_id
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()

    def delete_data(self, connect, table_name, id, id_type):
        if connect is None:
            return
        cursor = connect.cursor()
        try:
            delete_query = f'DELETE FROM {table_name} WHERE {id_type} = %s'
            cursor.execute(delete_query, (id,))
            connect.commit()
            print(f"{id_type} {id} from table '{table_name}' deleted successfully")
        except Error as e:
            print(f"Error while trying to delete record: {e}")
        finally:
            cursor.close()

    def get_data(self, connect, table_name, id, id_type):
        if connect is None:
            return
        cursor = connect.cursor()
        try:
            select_query = f'SELECT * FROM {table_name} WHERE {id_type} = %s'
            cursor.execute(select_query, (id,))
            data = cursor.fetchall()
            json_data = json.dumps(data, default=str)
            return data
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()

    def get_data_for_id(self, connect, table_name, id, id_type, framework_id):
        if connect is None:
            return
        cursor = connect.cursor()
        try:
            select_query = f'SELECT * FROM {table_name} WHERE {id_type} = %s AND framework_id = %s'
            cursor.execute(select_query, (id, framework_id))
            data = cursor.fetchall()
            return data
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()

    def get_all(self, connect, table_name):
        if connect is None:
            return
        cursor = connect.cursor()
        try:
            select_query = f'SELECT * FROM {table_name}'
            cursor.execute(select_query)
            data = cursor.fetchall()
            json_data = json.dumps(data, default=str)
            return data
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()

    def update_data(self, connect, table_name, id, field, data):
        if connect is None:
            return
        id_type = table_name[:-1] + '_id' if table_name.endswith('s') else table_name + '_id'
        cursor = connect.cursor()
        update_query = f'UPDATE {table_name} SET {field} = %s WHERE {id_type} = %s'
        try:
            cursor.execute(update_query, (data, id))
            connect.commit()
            print(f"'{field}' Field for {id_type} {id} updated successfully")
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()

    def CheckExistence(self, connection, table_name, id, id_type): 
        data = self.get_data(connection, table_name, id, id_type)
        exists = None
        if data:
            exists = True
        else:
            exists = False
        return exists
    
    def CheckExistenceAdvanced(self, connection, table_name, id, id_type, framework_id):
        data = self.get_data_for_id(connection, table_name, id, id_type, framework_id)
        exists = None
        if data:
            exists = True
        else:
            exists = False
        return exists


