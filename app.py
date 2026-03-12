from flask import Flask, render_template, request, redirect, url_for
from bson import ObjectId
from pymongo import MongoClient
import os

app = Flask(__name__)
title = "TODO sample application with Flask and MongoDB"
heading = "TODO Reminder with Flask and MongoDB"

# Pulls from EC2 environment variables; falls back to localhost if not found
mongo_uri = os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017")
client = MongoClient(mongo_uri)
db = client.mymongodb
todos = db.todo

def redirect_url():
    return request.args.get('next') or request.referrer or url_for('tasks')

@app.route("/list")
def lists():
    todos_l = todos.find()
    return render_template('index.html', a1="active", todos=todos_l, t=title, h=heading)

@app.route("/")
@app.route("/uncompleted")
def tasks():
    todos_l = todos.find({"done": "no"})
    return render_template('index.html', a2="active", todos=todos_l, t=title, h=heading)

@app.route("/completed")
def completed():
    todos_l = todos.find({"done": "yes"})
    return render_template('index.html', a3="active", todos=todos_l, t=title, h=heading)

@app.route("/done")
def done():
    id = request.values.get("_id")
    task = todos.find_one({"_id": ObjectId(id)})
    if task["done"] == "yes":
        todos.update_one({"_id": ObjectId(id)}, {"$set": {"done": "no"}})
    else:
        todos.update_one({"_id": ObjectId(id)}, {"$set": {"done": "yes"}})
    return redirect(redirect_url())

@app.route("/action", methods=['POST'])
def action():
    todos.insert_one({
        "name": request.values.get("name"),
        "desc": request.values.get("desc"),
        "date": request.values.get("date"),
        "pr": request.values.get("pr"),
        "done": "no"
    })
    return redirect("/list")

@app.route("/remove")
def remove():
    key = request.values.get("_id")
    todos.delete_one({"_id": ObjectId(key)})
    return redirect("/")

@app.route("/update")
def update():
    id = request.values.get("_id")
    task = todos.find({"_id": ObjectId(id)})
    return render_template('update.html', tasks=task, h=heading, t=title)

@app.route("/action3", methods=['POST'])
def action3():
    id = request.values.get("_id")
    todos.update_one({"_id": ObjectId(id)}, {'$set': {
        "name": request.values.get("name"),
        "desc": request.values.get("desc"),
        "date": request.values.get("date"),
        "pr": request.values.get("pr")
    }})
    return redirect("/")

@app.route("/search", methods=['GET'])
def search():
    key = request.values.get("key")
    refer = request.values.get("refer")
    if key == "_id":
        todos_l = todos.find({refer: ObjectId(key)})
    else:
        todos_l = todos.find({refer: key})
    return render_template('searchlist.html', todos=todos_l, t=title, h=heading)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
