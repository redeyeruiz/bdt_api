import pyodbc

class God:
    def __init__(self):
        self.__connection_str = 'Driver={ODBC Driver 17 for SQL Server};Server=tcp:bdt.database.windows.net,1433;Database=bdt;Uid=adminITC;Pwd={onlyfans123!};'
    
    def open_connection(self):
        return pyodbc.connect(self.__connection_str)

    def run_query(self, query, params_list):
        # Open a connection & create the cursor!
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute(query, params_list)

        rows = cursor.fetchall()

        # Close Connections
        cursor.close()
        conn.close()

        # Return results in a list
        return rows

    def run_insert(self, query, params_list):

        try:

            # Open a connection & create the cursor!
            conn = self.open_connection()
            cursor = conn.cursor()
            cursor.execute(query, params_list)

            # Commit & Close Connections
            conn.commit()
            cursor.close()
            conn.close()
            
            # Response is in dict form
            message = {"mensaje": "Recurso creado exitosamente!"}
            status = 201

        except pyodbc.Error as error:
            
            # Response is in dict form
            message = {"mensaje": "Error, Recurso ya existente en la base de datos!"}
            status = 409

        return message, status
