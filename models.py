import boto3
from botocore.exceptions import ClientError
import json
import random
import trackerutils


dynamodb = boto3.resource("dynamodb", region_name="us-west-1")

class User:
    db = dynamodb.Table("CheesyStickUsers")
    
    def __init__(self, username, password_hash="", salt="", phone_number=""):
        self.username = username
        self.password_hash = password_hash
        self.salt = salt
        self.phone_number = phone_number

    def save(self):
        # save to the database
        response = User.db.update_item(
            Key={
                "username": self.username
            },
            UpdateExpression="set password_hash = :ph, salt = :s, phone_number = :pn",
            ExpressionAttributeValues={
                ":ph": self.password_hash,
                ":s": self.salt,
                ":pn": self.phone_number
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
                    salt=password_hash_and_salt[1])

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
            if "phone_number" not in user:
                user["phone_number"] = ""
            return User(user["username"],
                        password_hash=user["password_hash"],
                        salt=user["salt"],
                        phone_number=user["phone_number"])
