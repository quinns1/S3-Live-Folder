#!/usr/bin/env python

"""
Project Name: AWS S3 Live Folder
Version: 1.0
Developed By: Shane Quinn
Course: Computer Science Project
Course: Higher Diploma in Cloud Computing
"""

import boto3
import S3
import Resources
import SQLite
import os
import time
import Encryptt
import sqlite3
import ntpath
import threading
import webbrowser
from sqlite3 import Error
from tkinter import *
from tkinter import ttk
from tkinter import messagebox


class S3_Live_Folder_GUI:

    def __init__(self, master):    
        """
        Initialise GUI and Class variables.
        """
        #Find program directory
        self.pd = os.path.dirname(os.path.abspath(__file__)).encode('unicode_escape').decode()
        self.sync = False
        self.checkflag = True
        self.run_flag = False   
        self.sync_var = IntVar()
        self.background_var = IntVar()
        self.number_transactions = 0
        self.bytes_used = 0 
        self.transactions_list = []
        self.bucket_objects = []
        self.folder_contents = []
        sql_create_loginDetails_table = """ CREATE TABLE IF NOT EXISTS loginDetails (
                                            bn text NOT NULL PRIMARY KEY,     
                                            ak text NOT NULL,   
                                            sak text NOT NULL
                                        ); """
        logindetailsdb = self.pd + "\\logindetails.db"
        self.logindetailsdbCont = SQLite.SQLiteController(logindetailsdb)     
        self.logindetailsdbCont.execute_sql(sql_create_loginDetails_table)
    
        """
        - Configure GUI for the first time.
        """
        master.title('S3 Live Folder')
        master.resizable(False, False)
        master.protocol('WM_DELETE_WINDOW', self.finish_program)
        menubar = Menu(master)
        helpmenu = Menu(menubar, tearoff=0)
        self.managemenu = Menu(menubar, tearoff=0)
        self.filemenu = Menu(menubar, tearoff=0)
        self.filemenu.add_command(label='Setup new connection', command=self.setup)
        self.filemenu.add_command(label='Reconnect', command=self.reconnect)
        self.filemenu.add_command(label='Quit', command=self.finish_program)
        menubar.add_cascade(label="File", menu=self.filemenu)
        self.managemenu.add_command(label='View Stats', command=self.view_stats, state=DISABLED)
        self.managemenu.add_command(label='Manage Users', command=self.manage_users)
        menubar.add_cascade(label="Manage", menu=self.managemenu)
        helpmenu.add_command(label='Help', command=self.open_help)
        menubar.add_cascade(label='Help', menu=helpmenu)
        master.config(menu=menubar)
        master.configure(background = '#ffffff')
        self.style = ttk.Style()
        self.style.configure('TFrame', background = '#ffffff')
        self.style.configure('TButton', background = '#ffffff')
        self.style.configure('TLabel', background = '#ffffff', font = ('Arial', 9))
        self.style.configure('Header.TLabel', font = ('Arial', 14, 'bold'))    
        self.root_window = master
        self.frame_header = ttk.Frame(self.root_window)
        self.frame_header.pack()
        try:
            master.iconbitmap(self.pd + r'\Images\S3_Icon.ico')
            self.logo = PhotoImage(file = self.pd + r'\Images\S3 Image.png').subsample(2, 2)
            ttk.Label(self.frame_header, image = self.logo).grid(row = 0, column = 0)
        except:
            pass
        ttk.Label(self.frame_header, font = "12", text = 'S3 Live Folder').grid(row = 0, column = 1)
        self.frame_content = ttk.Frame(self.root_window)
        self.frame_content.pack()
        self.home()


    def home(self):
        """
        - User chooses to Start new connection or Reconnect using previously saved login credentials
        """
        self.frame_content.pack_forget()
        self.frame_content = ttk.Frame(self.root_window)
        self.frame_content.pack()
        self.set_available_buttons()
        ttk.Label(self.frame_content, text = '\n\nPlease choose from one of the following options\n').grid(row = 0, column =0, columnspan=2, padx =5, sticky='s')
        ttk.Button(self.frame_content, text = 'Setup', command = self.setup ).grid(row = 1, column = 0, padx = 5, pady = 5, sticky = 'e')
        ttk.Button(self.frame_content, text = 'Reconnect', command = self.reconnect ).grid(row = 1, column = 1, padx = 5, pady = 5, sticky = 'w')
        

    def setup (self):
        """
        - Entry fields to enter access key, secret access key and bucket name. Connect button button.
        Background and sync checkboxes        
        """
        self.run_flag = False
        self.set_available_buttons()
        self.frame_content.pack_forget()
        self.checkflag = True
        self.frame_content = ttk.Frame(self.root_window)
        self.frame_content.pack()
        ttk.Label(self.frame_content, text = 'Please enter the following details').grid(row = 0, column = 0, columnspan = 2, padx = 5)
        ttk.Label(self.frame_content, text = 'Access Key:').grid(row = 1, column = 0, padx = 5, sticky = 'sw')
        ttk.Label(self.frame_content, text = 'Secret Access Key:').grid(row = 3, column = 0, padx = 5, sticky = 'sw')
        ttk.Label(self.frame_content, text = 'Bucket Name:').grid(row = 1, column = 1, padx = 5, sticky = 'sw')
        self.entry_ak = ttk.Entry(self.frame_content, width = 24)
        self.entry_sak = ttk.Entry(self.frame_content, width = 24)
        self.entry_bn = ttk.Entry(self.frame_content, width = 24)
        self.check_sync = ttk.Checkbutton(self.frame_content, text = "Sync with bucket", variable = self.sync_var)
        self.check_background = ttk.Checkbutton(self.frame_content, text = "Run in background", variable = self.background_var)
        self.entry_ak.grid(row = 2, column = 0, padx = 5)
        self.entry_sak.grid(row = 4, column = 0, padx = 5)
        self.entry_bn.grid(row = 2, column = 1, padx = 5)
        self.check_sync.grid(row = 4, column = 1, padx = 5, sticky = 'w')
        self.check_background.grid(row = 3, column = 1, padx=5, sticky = 'w')
        ttk.Button(self.frame_content, text = 'Connect', command = self.connect_first_time ).grid(row = 5, column = 1, padx = 5, pady = 5, sticky = 'w')
        ttk.Button(self.frame_content, text = 'Back', command = self.home ).grid(row = 5, column = 0, padx = 5, pady = 5, sticky = 'e')



    def connect_first_time (self):
        """"
        - Entry fields to enter access key, secret access key and bucket name and connect. Details are then saved in db
        """
        self.run_flag = True
        self.set_available_buttons()
        self.ak = format(self.entry_ak.get())
        self.sak = format(self.entry_sak.get())
        self.bn = format(self.entry_bn.get())  
        if self.check_sync.instate(['selected']):   # Is sync checked
            self.sync = True
        successful = False            
        if self.checkflag == True:
            res = Resources.Resource(self.ak, self.sak)
            s3 = res.S3Resource()
            s3cont = S3.S3Controller(s3)
            if s3cont.connection_successful(self.bn, self.pd):
                self.number_transactions += 2
                self.transactions_list.append("Connection to '%s' has been successful" % (self.bn))
                logindetails = (self.bn, self.ak, self.sak)
                self.logindetailsdbCont.loginDetails_entry(logindetails)
                self.checkflag = False
                if self.check_background.instate(['selected']):
                    self.root_window.destroy()
                    S3_Live_Folder_GUI.Live_Folder(self)
                self.S3_Live_thread = threading.Thread(target=S3_Live_Folder_GUI.Live_Folder,
                                                    args=(self,))
                self.S3_Live_thread.start()
                successful = True
            else:
                messagebox.showinfo("Unsuccessful", "Please enter valid details and try again.")
        if successful == True:
            self.running()   
        else:
            self.setup()       
        
   

    def running(self):
        """
        - Normal Running window
        Indeterminate progress bar & Stop Button
        """
        
        self.frame_content.pack_forget()
        self.frame_content = ttk.Frame(self.root_window)
        self.frame_content.pack()
        ttk.Button(self.frame_content, text = 'Stop', command = self.setup ).grid(row = 1, column = 1, padx = 5, pady = 5, sticky = 'e')
        progressbar = ttk.Progressbar(self.frame_content, orient = HORIZONTAL, length = 200)
        progressbar.grid(row = 1, column = 0, padx = 5, pady = 5)
        progressbar.config(mode = 'indeterminate')
        progressbar.start()


    def reconnect(self):
        """
        - Allow user to choose previously saved bucket and connect
        Background and Sync checkboxes also available
        """
        self.run_flag = False
        self.set_available_buttons()
        self.checkflag = True
        self.frame_content.pack_forget()
        self.frame_content = ttk.Frame(self.root_window)
        self.frame_content.pack()
        ttk.Label(self.frame_content, text = 'Choose Bucket').grid(row = 0, column = 0, padx = 5, sticky = 'sw')
        self.listbox = Listbox(self.frame_content, height =5, width = 30)
        self.listbox.grid(row=1,column=0, rowspan=5)
        buckets = self.logindetailsdbCont.get_all_buckets_loginDetais()
        for bucket in buckets :
            self.listbox.insert(END, bucket)
        self.check_sync = ttk.Checkbutton(self.frame_content, text = "Sync with bucket", variable = self.sync_var)
        self.check_background = ttk.Checkbutton(self.frame_content, text = "Run in background", variable = self.background_var)
        self.check_sync.grid(row = 5, column = 1, padx = 5, sticky = 'w')
        self.check_background.grid(row = 4, column = 1, padx=5, sticky = 'w')
        ttk.Button(self.frame_content, text = 'Connect', command = self.connect ).grid(row = 7, column = 1, padx = 5, pady = 5, sticky = 'w')
        ttk.Button(self.frame_content, text = 'Back', command = self.home ).grid(row = 7, column = 0, padx = 5, pady = 5, sticky = 'e')



    def connect(self):
        """
        - Take selected bucket from listbox, query logindetails table and retrieve login credentials
        test connection, if successful start second thread of main program (Live_Folder)
        If Background is checked close root window after starting second thread
        If Sync is selected set Sync flag = True
        """
        self.run_flag = True
        self.set_available_buttons()
        self.bn = self.listbox.get(ACTIVE)
        logindetails = self.logindetailsdbCont.get_login_credentials(self.bn)
        self.ak = logindetails[0]
        self.sak = logindetails[1]
        if self.check_sync.instate(['selected']):   # Is sync checked
            self.sync = True
        successful = False            
        if self.checkflag == True:
            res = Resources.Resource(self.ak, self.sak)
            s3 = res.S3Resource()
            s3cont = S3.S3Controller(s3)
            if s3cont.connection_successful(self.bn, self.pd):
                self.number_transactions += 2
                self.transactions_list.append("Connection to '%s' has been successful" % (self.bn))
                logindetails = (self.bn, self.ak, self.sak)
                self.logindetailsdbCont.loginDetails_entry(logindetails)
                self.checkflag = False
                if self.check_background.instate(['selected']):
                    self.root_window.destroy()
                    S3_Live_Folder_GUI.Live_Folder(self)
                self.S3_Live_thread = threading.Thread(target=S3_Live_Folder_GUI.Live_Folder,
                                                    args=(self,))
                self.S3_Live_thread.start()
                successful = True
            else:
                messagebox.showinfo("Unsuccessful", "Please enter valid details and try again.")
                
        if successful == True:
            self.running()   
        else:
            self.setup()

      
    def manage_users(self):
        """
        - Allow user to add/delete accounts from the application
        Displays DB and if user deletes entry, it's deleted from the table.
        """
        self.frame_content.pack_forget()
        self.frame_content = ttk.Frame(self.root_window)
        self.frame_content.pack()
        self.listbox = Listbox(self.frame_content, height =5, width = 30)
        self.listbox.grid(row=1,column=0, rowspan=5)
        buckets = self.logindetailsdbCont.get_all_buckets_loginDetais()
        for bucket in buckets :
            self.listbox.insert(END, bucket)
        ttk.Button(self.frame_content, text = 'Remove Selected', command = self.remove_selected ).grid(row = 6, column = 1, padx = 5, pady = 5, sticky = 'w')
        ttk.Button(self.frame_content, text = 'Home', command = self.home ).grid(row = 2, column = 1, padx = 5, pady = 5, sticky = 'e')


    def remove_selected(self):
        """
        - Remove selected login details from SQLite table
        """
        delete_bucket = self.listbox.get(ACTIVE)
        self.logindetailsdbCont.delete_loginDetails_entry(delete_bucket)
        self.manage_users()
    

    def view_stats(self):
        """
        Displays the following information:
           * Size of memory used
           * Number of Transactions since program started
           * Recent Transactions
           * Bucket contents
           * Folder Contents
        """
        self.frame_content.pack_forget()
        self.frame_content = ttk.Frame(self.root_window)
        self.frame_content.pack()
        self.frame_details = ttk.Frame(self.frame_content, height = 200, width = 400)
        self.frame_transactions = ttk.Frame(self.frame_content, height = 200, width = 500)
        self.frame_bc = ttk.Frame(self.frame_content, height = 200, width = 400)
        self.frame_fc = ttk.Frame(self.frame_content, height = 200, width = 400)
        self.frame_details.grid(row = 1, column =1)
        self.frame_transactions.grid(row = 0, column =1)
        self.frame_bc.grid(row = 1, column =0)
        self.frame_fc.grid(row = 0, column =0)
        self.frame_transactions.grid_propagate(False)
        self.frame_details.grid_propagate(False)
        self.frame_bc.grid_propagate(False)
        self.frame_fc.grid_propagate(False)
        ttk.Label(self.frame_details, text = 'Memory Used (KB): ').grid(row = 0, column =0, padx =5, sticky='s')
        ttk.Label(self.frame_details, text = self.bytes_used).grid(row = 0, column =1, padx =5, sticky='s')
        ttk.Label(self.frame_details, text = 'Transactions since starting: ').grid(row = 1, column =0, padx =5, sticky='s')
        ttk.Label(self.frame_details, text = self.number_transactions).grid(row = 1, column =1, padx =5, sticky='s')
        ttk.Button(self.frame_details, text = 'Return', command = self.running ).grid(row = 5, column = 0, padx = 5, pady = 5, sticky = 's')
        ttk.Button(self.frame_details, text = 'Reload', command = self.view_stats).grid(row = 5, column = 1, padx = 5, columnspan=5, pady = 5, sticky = 's')
        

        transactions_string = '\t\t\tRecent Transactions\n--------------------------------------------------------------\n'
        for i in self.transactions_list:
            transactions_string += i + "\n"
        transactions_box = Text(self.frame_transactions)
        transactions_box.insert(INSERT, transactions_string)
        transactions_box.grid(row = 0, column = 0, padx = 5, pady = 5)     

        bc_string = '\t\tBucket Contents\n--------------------------------------------------------------\n'
        for i in self.bucket_objects:
            bc_string += i + "\n"
        bc_box = Text(self.frame_bc)
        bc_box.insert(INSERT, bc_string)
        bc_box.grid(row = 0, column = 0, padx = 5, pady = 5)     

        fc_string = '\t\tFolder Contents\n--------------------------------------------------------------\n'
        for i in self.folder_contents:
            fc_string += i + "\n"
        fc_box = Text(self.frame_fc)
        fc_box.insert(INSERT, fc_string)
        fc_box.grid(row = 0, column = 0, padx = 5, pady = 5)     



    def set_available_buttons(self):
        """
        - Set what options are avabilable in the menu when the UI changes state
        """
        if self.run_flag == True:
            self.managemenu.entryconfig('View Stats', state=NORMAL)
            self.filemenu.entryconfig('Setup new connection', state=DISABLED)
            self.filemenu.entryconfig('Reconnect', state=DISABLED)
            self.managemenu.entryconfig('Manage Users', state=DISABLED)
        else:
            self.managemenu.entryconfig('View Stats', state=DISABLED)
            self.filemenu.entryconfig('Setup new connection', state=NORMAL)
            self.filemenu.entryconfig('Reconnect', state=NORMAL)
            self.managemenu.entryconfig('Manage Users', state=NORMAL)


    def open_help(self):
        """
        - Open Interactive HTML Help menu.
        """
        helpurl = self.pd + '\\Help\\Help.html'
        if os.path.isfile(helpurl):
            webbrowser.open(helpurl, new=1)
        else:
            messagebox.showinfo("Not Available", "Help folder is not in same directory as application")


    def finish_program(self):
        """
        - Quit the program by ending all threads
        """
        self.run_flag = False
        self.root_window.quit()


    def Live_Folder(self):

        """ 
        ###############################################################################################################
                                                    SETUP
        ###############################################################################################################
        """
        filedetailsdb = self.pd + r"\filedetails.db"
        folder_name = self.pd + r"\S3_Live_Folder"
        sql_create_fileDetails_table = """ CREATE TABLE IF NOT EXISTS fileDetails (
                                            s3key text PRIMARY KEY,
                                            fileName text NOT NULL,
                                            size integer,   
                                            uploaded boolean,
                                            deleted boolean     
                                        ); """
        """
        Set up S3
        """
        res = Resources.Resource(self.ak, self.sak)
        s3 = res.S3Resource()
        s3cont = S3.S3Controller(s3)
        encryptionCont = Encryptt.EncryptionCont(self.sak, self.pd)

        """
        If S3_Live_Folder isn't present, create folder
        """    
        folder_present = False
        entries = os.listdir(self.pd)
        for entry in entries :
            if entry == "S3_Live_Folder" :
                folder_present = True
        if folder_present == False :
            os.makedirs(folder_name)
        
        """
        Create SQLite fileDetails table if not already created
        """
        filedetailsdbCont = SQLite.SQLiteController(filedetailsdb)      
        filedetailsdbCont.execute_sql(sql_create_fileDetails_table)


        """ 
        ###############################################################################################################
                                                        Main Loop
        ###############################################################################################################
        """

        while self.run_flag == True:
            self.folder_contents = os.listdir(folder_name)
            """
            Check if any files have been added to the folder
            - Iterate through files
            If the file is not present in the database
            Add to database
            """
            file_there = False
            for entry in self.folder_contents:          
                file_there = filedetailsdbCont.file_in_database(entry)
                if file_there == False:
                    file_name_wdir = folder_name + "\\" + entry
                    file_size = os.stat(file_name_wdir).st_size
                    file_name = (entry.split(".")[0]) 
                    file_info = (entry, file_name, file_size, False, False)
                    filedetailsdbCont.fileDetails_entry(file_info)
                    

            """
            Check if any files have changed size
            - Iterate through files
            If filesize is different from saved file size in database
            Set 'uploaded' fieled to False.
            """
            for entry in self.folder_contents:      
                file_name_wdir = folder_name + "\\" + entry
                file_size = os.stat(file_name_wdir).st_size
                database_file_size = filedetailsdbCont.get_file_size(entry)
                if file_size != database_file_size:
                    filedetailsdbCont.update_fileDetails_size(file_size, entry)
                    filedetailsdbCont.update_fileDetails_uploaded(entry, False)

            """
            Encrypt and upload any files which have haven't been uploaded yet
            - Iterate through files
            if 'uploaded' field = False, upload to bucket and set 'uploaded' field = True
            """
            for entry in self.folder_contents:              
                has_been_uploaded = filedetailsdbCont.has_file_been_uploaded(entry)
                if has_been_uploaded == False:
                    file_name_wdir = folder_name + "\\" + entry
                    ef = encryptionCont.encrypt(file_name_wdir)
                    self.transactions_list.append(s3cont.upload_object(self.bn, ef , entry))
                    self.number_transactions += 1
                    os.remove(ef)
                    filedetailsdbCont.update_fileDetails_uploaded(entry, True)

            """
            Have any files have been deleted:
            -iterate through list of keys
            compare each key to list of files in directory
            If key is not in directory set deleted flag high
            """
            db_keys = filedetailsdbCont.get_all_keys()
            for key in db_keys:
                deleted = True
                for entry in self.folder_contents :           
                    if key == entry :
                        deleted = False
                if deleted == True:
                    filedetailsdbCont.update_fileDetails_deleted(key, True)


            """
            Delete any files from S3 bucket and database which have been deleted from folder
            - iterate through database keys
            if deleted flag is True, delete from bucket, -delete from database
            """
            for key in db_keys :
                deleted = filedetailsdbCont.has_file_been_deleted(key)
                if deleted == True:
                    self.transactions_list.append(s3cont.delete_object(self.bn, key))
                    self.number_transactions += 1
                    filedetailsdbCont.delete_fileDetails_entry(key)


            """
            Here we download objects from S3 that aren't on already in folder, if the user specifies to
            """
            self.bucket_objects = s3cont.get_objects(self.bn)     
            if self.sync == True:
                for obj in self.bucket_objects :
                    if obj not in self.folder_contents:                     
                        original_fn = folder_name + "\\" + obj
                        ef = (original_fn.split(".")[0]) + ".encrypted"
                        self.transactions_list.append(s3cont.download_object(self.bn, obj, ef))
                        self.number_transactions += 1
                        if encryptionCont.is_encrypted(ef):
                        #If file is encrypted decrypt before adding to db
                            df = encryptionCont.decrypt(ef)
                            os.remove(ef)
                            file_size = os.stat(df).st_size     #Gets file size                    
                            df = ntpath.basename(df)            #Trims Directory
                            file_name = (df.split(".")[0])      #Trims Extentsion   
                            file_info = (df, file_name, file_size, True, False)
                            filedetailsdbCont.fileDetails_entry(file_info)   
                        else:
                        # If file is not encrypted add to db
                            os.rename(ef, original_fn)
                            file_size = os.stat(original_fn).st_size
                            original_fn = ntpath.basename(original_fn)  #Trims path (C://example//etc)
                            file_name = (original_fn.split(".")[0])     # Trims extension (.txt, .xcl etc)
                            file_info = (original_fn, file_name, file_size, True, False)
                            filedetailsdbCont.fileDetails_entry(file_info) 
 

                """
                Here we check if any files have been deleted from S3 and delete from host if so
                - iterate through db keys, if key not in bucket delete from db and S3_Live_Folder
                """      
                for key in db_keys:
                    if key not in self.bucket_objects :
                        filedetailsdbCont.delete_fileDetails_entry(key)
                        folder_name + key
                        try:
                            os.remove(folder_name + "\\" + key)
                            t = ("'%s' has been deleted from S3_Live_Folder\n" % (key))
                            self.transactions_list.append(t)
                        except:
                            #File has been deleted on host already
                            pass

                
            self.bytes_used = s3cont.get_bytes_used(self.bn)        #Update bytes used

            #Only show 5 transactions
            while len(self.transactions_list) > 5:
                self.transactions_list.pop(0)


            """
            Rest for 4 seconds so as to not waste CPU resources
            """
            time.sleep(4)

            


def main():            
    """
    - Here the root UI window is created and passed into our program
    """
    root = Tk()
    S3_Live_Folder_GUI(root)
    root.mainloop()


if __name__ == "__main__": main()
