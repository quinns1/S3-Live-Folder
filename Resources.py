import boto3

class Resource:
  
  
    def __init__(self, ak, sk) :
        """
        - Resource Instance, takes in access key and secret key to form connection with AWS 
        :param ak: access key to connect to AWS account
        :param sk: secret access key to connect to AWS accoutnt
        """
        self.region = "eu-west-1"
        self.key_id = ak
        self.secret_key = sk

    def S3Resource(self): 
        """
        - Create and return a Resource for interacting with S3 instances
        :return s3: resource for interacting with S3 instances
        """
        s3 = boto3.resource("s3",
                             aws_access_key_id=self.key_id ,
                             aws_secret_access_key=self.secret_key,
                             region_name=self.region
                            )  
        return s3

