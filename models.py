import boto3
from botocore.exceptions import ClientError
import json
import random
import trackerutils


dynamodb = boto3.resource("dynamodb", region_name="us-west-1")

class User:
    db = dynamodb.Table("CheesyStickUsers")
    
    def __init__(self, username, password_hash="", salt="", profile_picture=""):
        self.username = username
        self.password_hash = password_hash
        self.salt = salt
        self.profile_picture = profile_picture

    def save(self):
        # save to the database
        response = User.db.update_item(
            Key={
                "username": self.username
            },
            UpdateExpression="set password_hash = :ph, salt = :s, profile_picture = :pp",
            ExpressionAttributeValues={
                ":ph": self.password_hash,
                ":s": self.salt,
                ":pp": self.profile_picture
            },
            ReturnValues="UPDATED_NEW"
        )
        return

    def create(username, password):
        # create a new User in the db
        password_hash_and_salt = trackerutils.get_password_hash_and_salt(password)
        response = User.db.put_item(
            Item={
                "username": username,
                "password_hash": password_hash_and_salt[0],
                "salt": password_hash_and_salt[1],
            },
            ConditionExpression="attribute_not_exists (username)"
        )
        return User(username,
                    password_hash=password_hash_and_salt[0],
                    salt=password_hash_and_salt[1],
                    profile_picture="")

    def by_username(username):
        # get from the database and return a User object
        try:
            response = User.db.get_item(
                Key={
                    "username": username
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            user = response["Item"]
            try:
                return User(user["username"],
                            password_hash=user["password_hash"],
                            salt=user["salt"],
                            profile_picture=user["profile_picture"])
            except:
                return User(user["username"],
                            password_hash=user["password_hash"],
                            salt=user["salt"],
                            profile_picture="")
