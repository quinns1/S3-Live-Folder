import sqlite3
from sqlite3 import Error

class SQLiteController :

    def __init__(self, db) :
        """
        - Instance creating connection to SQLite datbase.
        :param db: database name + location    
        """
        database = db
        self.conn = None
        try:
            self.conn = sqlite3.connect(database)
        except Error as e:
            print(e)
            

    def execute_sql (self, sql):
        """
        - Execute SQL command 
        :param sql: sql command to be executed
        """
        try:
            c = self.conn.cursor()
            with self.conn : 
                c.execute(sql)
        except Error as e:
            print(e)


    def fileDetails_entry(self, entry):
        """
        - Create a new entry into the fileDetails table
        :param entry:   Entry details
        """
        sql = ''' INSERT INTO fileDetails(s3key, fileName, size, uploaded, deleted)
                VALUES(?,?,?,?,?) '''
        try :
            c = self.conn.cursor()
            with self.conn :        
                c.execute(sql, entry)
        except Error as e:
            print(e)


    def delete_fileDetails_entry(self, s3key):
        """
        -  Delete an entry from 
        :param conn:  Connection to the SQLite database
        :param s3key:  unique id of entry, key used to identify file on s3
        """
        sql = 'DELETE FROM fileDetails WHERE s3key=?'
        c = self.conn.cursor()
        with self.conn : 
            c.execute(sql, (s3key,))
            self.conn.commit()
    

    def update_fileDetails_uploaded(self, s3key, uploaded):
        """
        -  Update Uploaded (boolean which is True if file has been uploaded to s3 bucket)
        :param conn:    Connection to the SQLite database
        :param uploaded: boolean of what you want to set uploaded to for given key, true if file has been uploaded to S3 bucket   
        """
        sql = ''' UPDATE fileDetails
                SET uploaded = ? 
                WHERE s3key = ?'''
        c = self.conn.cursor()
        c.execute(sql, (uploaded, s3key))
        self.conn.commit()


    def has_file_been_uploaded(self, s3key):
        """
        - Checks database and returns '1' if file has been uploaded and '0' if file hasn't been uploaded yet
        :param s3key: unique identifier of file and Primary key in SQLite database
        :return a: Boolean true if file has already been uploaded to S3 bucket
        """
        sql = '''SELECT uploaded
                FROM fileDetails
                WHERE s3key = ?'''
        uploaded = False
        try :
            c = self.conn.cursor()
            with self.conn :        
                c.execute(sql, (s3key,))
                uploaded = c.fetchall()    
                for i in uploaded:      #Parse boolean from array and list it's fetchall gets.
                    for a in i:
                        return a
        except Error as e:
            print(e)
            return e
    

    def file_in_database(self, filename):
        """
        - Check if file 'filename' is in database, return boolean true if yes or false if not.
        :param filename: Name of file in question
        :return present: True if file is present in database
        """

        sql = '''SELECT s3key
                FROM fileDetails'''
        keys = False
        try :
            c = self.conn.cursor()
            with self.conn :        
                c.execute(sql,)
                keys = c.fetchall()    
                for i in keys: 
                    for a in i:
                        if a == filename:
                            return True
            return False
        except Error as e:
            print(e)
            return e


    def get_file_size(self, s3key):
        """
        - Takes in S3Key, returns file size
        :param s3key: unique identifier of file and Primary key in SQLite database
        :return file_size: Size of file in bytes
        """
        sql = '''SELECT size
                FROM fileDetails
                WHERE s3key = ?'''
        try :
            c = self.conn.cursor()
            with self.conn :        
                c.execute(sql, (s3key,))
                file_size = c.fetchall()    
                for i in file_size:      #Parse size
                    for a in i:
                        return a
        except Error as e:
            print(e)
            return e


    def update_fileDetails_size(self, size, s3key):
        """
        - Update fileDetails entry 'size' parameter
        :param size: New size pararmeter
        :param s3key: Unique identifier of file and Primary key in SQLite database
        """
        sql = ''' UPDATE fileDetails
                SET size = ? 
                WHERE s3key = ?'''
        c = self.conn.cursor()
        c.execute(sql, (size, s3key))
        self.conn.commit()


    def has_file_been_deleted(self, s3key):
        """
        - Checks database and returns '1' if file has been uploaded and '0' if file hasn't been uploaded yet
        :param s3key: unique identifier of file and Primary key in SQLite database
        :return a: Boolean true if file has already been uploaded to S3 bucket
        """
        sql = '''SELECT deleted
                FROM fileDetails
                WHERE s3key = ?'''
        uploaded = False
        try :
            c = self.conn.cursor()
            with self.conn :        
                c.execute(sql, (s3key,))
                uploaded = c.fetchall()    
                for i in uploaded:      
                    for a in i:
                        return a
        except Error as e:
            print(e)
            return e
            

    def update_fileDetails_deleted(self, s3key, deleted):
        """
        -  Update Uploaded (boolean which is True if file has been uploaded to s3 bucket)
        :param conn:    Connection to the SQLite database
        :param uploaded: boolean of what you want to set uploaded to for given key, true if file has been uploaded to S3 bucket   
        """
        sql = ''' UPDATE fileDetails
                SET deleted = ? 
                WHERE s3key = ?'''
        c = self.conn.cursor()
        c.execute(sql, (deleted, s3key))
        self.conn.commit()


    def get_all_keys(self):
        """
        - Takes in S3Key, returns file size
        :param s3key: unique identifier of file and Primary key in SQLite database
        :return file_size: Size of file in bytes
        """
        sql = '''SELECT s3key
                FROM fileDetails'''
        keys_list = []
        try :
            c = self.conn.cursor()
            with self.conn :        
                
                c.execute(sql,)
                keys = c.fetchall()   
                for i in keys:     
                    for a in i:
                        keys_list.append(a)
                return keys_list
        except Error as e:
            print(e)
            return e


    def loginDetails_entry(self, entry):
        """
        - Create a new entry into the loginDetails table
        :param entry:   Entry details
        """
        sql = ''' INSERT INTO loginDetails(bn, ak, sak)
                VALUES(?,?,?) '''
        try :
            c = self.conn.cursor()
            with self.conn :        
                c.execute(sql, entry)
        except Error as e:
            print(e)


    def delete_loginDetails_entry(self, bn):
        """
        -  Delete an entry from loginDetails
        :param conn:  Connection to the SQLite database
        :param bn:  Bucketname of the saved details we wish to delete
        """
        sql = 'DELETE FROM loginDetails WHERE bn=?'
        c = self.conn.cursor()
        with self.conn : 
            c.execute(sql, (bn,))
            self.conn.commit()


    def get_all_buckets_loginDetais(self):
        """
        - Return list of buckets in loginDetails table
        return buckets: List of all buckets in table
        """
        sql = '''SELECT bn
                FROM loginDetails'''
        bucket_list = []
        try :
            c = self.conn.cursor()
            with self.conn :        
                c.execute(sql,)
                buckets = c.fetchall()   
                for i in buckets:     
                    for a in i:
                        bucket_list.append(a)
                return bucket_list
        except Error as e:
            print(e)
            return e


    def get_login_credentials(self, bn):
        """
        - Return AWS access key and secret access key from given bucketname
        :param bn: Bucketname
        :return details: access key and secret access key
        """
        sql = '''SELECT ak, sak 
                FROM loginDetails
                WHERE bn=?'''

        try :
            c = self.conn.cursor()
            with self.conn :        
                c.execute(sql, (bn,))
                details = c.fetchall()  
                for a in details:
                    return a    
        except Error as e:
            print(e)
            return e