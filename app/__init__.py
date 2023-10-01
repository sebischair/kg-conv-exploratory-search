# -*- coding: utf-8 -*-

from flask import Flask
from flask_dialogflow.agent import DialogflowAgent
from neo4j import GraphDatabase
from pymongo import MongoClient
from datetime import datetime

# create app and agent instances
app = Flask(__name__)
agent = DialogflowAgent(app=app, route="/", templates_file="templates/responses.yaml")
# driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password1"))
driver = GraphDatabase.driver("neo4j+s://12345.databases.neo4j.io:7687",
                              auth=("neo4j", "abcde123"))

mongo_uri = "mongodb+srv://user:pw@news-agent-logs.abcde123.mongodb.net/test"
client = MongoClient(mongo_uri)
db = client["logs_database"]
logs_collection = db["logs"]
state_collection = db['state']


# set up test route
@app.route("/")
def index():
    return "<h1>News Agent Backend</h1>"


# import main conversation handlers for webhooks
from app import webhooks
