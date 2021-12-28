import boto3
import os

class S3Controller:
    #Class for controlling S3 service

    def __init__(self, s3res):
        """
        - S3 Controller constructor
        :param s3res: S3 resource for interacting with S3
        """
        self.s3 = s3res


    def upload_object (self, bucket_name, file_name, key ):
        """
        - Upload the file 'file_name' to S3 storage, into bucket 'bucket_name'. 'key' will be unique s3 reference key
        :param bucket_name: Specifies bucket in S3 to be used
        :param file_name: Name of the file to be uplaoded
        :param key: Unique key used to identify object in S3 bucket.
        :return transaction: details on transaction.
        """
        try:
            bucket = self.s3.Bucket(bucket_name)
            bucket.upload_file(file_name, key)
            transaction = ("'%s' has been uploaded successfully to S3" % (key))
        except:         
            transaction = ("File has not been uploaded successfully, Please enter valid details next time.\n")
        return transaction


    def download_object (self, bucket_name, key, local_file_name ):
        """
        - Download the file referenced by 'key' from the bucket named 'bucket_name'. To the file location 'local_file_name'
        :param bucekt_name: Specifies bucket in S3 to be used
        :param key: Unique key used to identify object in S3
        :param local_file_name: Location/name of how the file will be stored on the users 
        :return transaction: details on transaction
        """
        #Download the file referenced by 'key' from the bucket named 'bucket_name'
        #to the file location 'local_file_name'
        try:
            self.s3.Bucket( bucket_name ).download_file( key, local_file_name)
            transaction = ("'%s' has been downloaded successfully from S3" % (key))
        except:         #If invalid information is given, print error message
            transaction = ("File has not been downloaded successfully, Please enter valid details next time.")
        return transaction
        

    def delete_object (self, bucket_name, key) :
        """
        - Delete the file referenced by 'key' from the bucket 'bucket_name'
        :param s3res: S3 resource for interacting with S3
        :param key: Unique key referencing file to be deleted
        """
        bucket = self.s3.Bucket( bucket_name)
        try:
            bucket.delete_objects(
                Delete={
                    "Objects":[
                        {
                            "Key":key
                        }
                    ]
                }
            )
            transaction = ("'%s' has been successfully deleted from S3" % (key))
        except :            #If invalid information is given, print error message
            transaction("File has not bee successfully deleted, please enter valid details next time")
        return transaction
        

    def get_objects (self, bucket_name) :
        """
        - Returns List of all objects in a given S3 bucket
        :param bucket_name: Specifies bucket in S3 to be used
        :return bucket_list: list of all objects in bucket
        """
        try:
            bucket_list = []
            for bucket_object in self.s3.Bucket(bucket_name).objects.all():
                bucket_list.append(bucket_object.key)
            return bucket_list
        except:         
            print("Please enter a valid Bucket name next time")
    
    
    def connection_successful(self, bucket_name, directory):
        """
        - Test connection by uploading program to AWS and deleting it
        """
        try:
            key = "test127"
            testfile = directory + "\\connectiontest.txt"
            upload = open(testfile, "w+")
            upload.close()
            bucket = self.s3.Bucket(bucket_name)
            bucket.upload_file(testfile, key)
            bucket.delete_objects(
                Delete={
                    "Objects":[
                        {
                            "Key":key
                        }
                    ]
                }
            )
            os.remove(testfile)
            return True
        except:  
            try:
                os.remove(testfile)
            except:
                pass
            return False
        
        
    def get_bytes_used(self, bucket_name):
        """
        - Returns total amount of memory used in bucket
        :param bucket_name: Name of bucket
        :return bytes_used: Number of bytes used in bucket.
        """

        try:
            bytes_used = 0
            for bucket_object in self.s3.Bucket(bucket_name).objects.all():
                bytes_used += bucket_object.size
            return bytes_used
        except:         
            print("Invalid Bucket Name")