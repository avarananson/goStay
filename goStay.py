from pymongo import MongoClient
from flask import Flask, render_template


# client = MongoClient('localhost', 27017)
# db = client.test_db
# posts = db.posts


app  = Flask(__name__)

@app.route("/")
def trial():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)


