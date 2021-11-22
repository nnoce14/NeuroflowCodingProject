import os
from datetime import datetime
from csv import reader, writer
from flask import Flask, jsonify, g, abort, request, url_for
from flask_restful import Api, Resource, reqparse
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'my super secret key is super long and secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# global moods dictionary for all users
moods = {}

# Models
class User(db.Model):
    # Sets up the SQLite database that holds the user information
    # id is an integer and is the primary key
    # username is a 32 length string which holds the user's username in plaintext
    # password_hash is a 128 length string which holds a hashed version of the user's password
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime)
    streak = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.streak = 0
        self.timestamp = None

    # uses the provided hashing method from Werkzeug.security to hash the plaintext password
    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    # verifies a plaintext password using the user's password_hash and a provided verification
    # method from the Werkzeug.security library
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    

# HTTPBasicAuth Security
@auth.verify_password
def verify_password(username, password):
    # grabs relevant user from users table
    user = User.query.filter_by(username=username).first()
    # user doesn;t exist or password received does not match the user's password_hash
    if not user or not user.verify_password(password):
        return False
    # sets the current session user to that user
    g.user = user
    return True

# Creates request parser for POST request to /api/mood endpoint
# Requires a string argument with a key of mood to be passed into the request
moodParser = reqparse.RequestParser()
moodParser.add_argument('mood', type=str, help='No mood entered...')

# Endpoints
@app.route('/api/mood', methods=['GET'])
@auth.login_required
def get_moods():
    # returns the mood list for the current session user
    return jsonify({'moods': moods[g.user.id]})

# reads the stored moods from 'moods.csv' and stores in dictionary to hold all users' moods
def add_stored_moods_to_local_moods():
    with open('moods.csv', 'r') as csv_file:
        csv_reader = reader(csv_file)
        userID = 1;
        for row in csv_reader:
            moods[userID] = row
            userID += 1

@app.route('/api/mood', methods=['POST'])
@auth.login_required
def add_mood():
    # gets the mood argument from the JSON object in the POST request
    args = moodParser.parse_args()
    mood = args['mood']
    if mood is None:
        return jsonify({'message': 'No mood entered'}), 400
    else: 
        now = datetime.now()
        # checks if first time sending a POST for this user
        if g.user.timestamp != None:
            # timestamp exists, so checks if this new POST is longer than 24 hours apart from
            # the stored timestamp of the user
            if more_than_24_hours_apart(g.user.timestamp, now):
                # resets the user's streak
                g.user.streak = 1
            # checks if new POST request is the day after the stored timestamp of the user
            elif next_day(g.user.timestamp, now):
                # increments the streak because user POSTed on consecutive days
                g.user.streak += 1
        else:
            # sets the streak to 1 because user POSTed for the first time
            g.user.streak = 1

        # overwrites the last timestamp with timestamp of the new request
        g.user.timestamp = now
        moods[g.user.id].append(mood)
        # writes back to csv file
        write_local_moods_back_to_stored_moods()
        return jsonify({'mood': mood}), 201

# checks if two datetime objects are greater than 24 hours apart
def more_than_24_hours_apart(datetime1, datetime2):
    return (datetime2 - datetime1).total_seconds() > 86400

# checks if one datetime object is the day after another datatime object
def next_day(datetime1, datetime2):
    return (datetime2.day - datetime1.day) == 1


@app.route('/api/users', methods=['POST'])
def new_user():
    # pulls the username and password arguments from the JSON object in the POST request
    username = request.json.get('username')
    password = request.json.get('password')
    # aborts if either argument not found
    if username is None or password is None:
        abort(400)
    # aborts if username already exists in the users table
    if User.query.filter_by(username=username).first() is not None:
        abort(400)
    # creates new user with username and hashes the entered password
    user = User(username=username)
    user.hash_password(password)
    # adds user to the database and commits the changes
    db.session.add(user)
    db.session.commit()
    # creates an empty mood list for the new user with the user's id as the key
    moods[user.id] = []
    return (jsonify({'username':user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})

@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    # aborts if user does not exist
    if not user:
        abort(400)
    # returns user's username, streak, and timestamp in JSON object
    return {'username': user.username, 'streak': user.streak, 'timestamp': user.timestamp}, 200

@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    # aborts if user does not exist
    if not user:
        abort(400)
    userID = user.id
    # deletes user from the database and commits the changes
    db.session.delete(user)
    db.session.commit()
    # removes the key of the user's id from the global moods dictionary
    del moods[userID]
    return jsonify({'success': True})

def initialize_moods():
    # grabs all of the users in the database
    users = User.query.all()
    for user in users:
        # creates empty list for each user who does not have an entry in the global moods dict
        # this means that the user does not have any moods stored in the 'moods.csv' file
        if user.id not in moods:
            moods[user.id] = []

def write_local_moods_back_to_stored_moods():
    with open('moods.csv', 'w') as csv_file:
        csv_writer = writer(csv_file)
        # grabs all of the users in the database
        users = User.query.all()
        # writes the global moods dictionary to the 'moods.csv', reflecting any changes made
        # during the session 
        for user in users:
            row = moods[user.id]
            csv_writer.writerow(row)

if __name__ == "__main__":
    # creates the required files 'db.sqlite' and 'moods.csv' if they do not already exist
    if not os.path.exists('db.sqlite'):
        db.create_all()
    if not os.path.exists('moods.csv'):
        fp = open('moods.csv', 'x')
        fp.close()

    # pulls the mood lists from 'moods.csv' and stores in global moods dictionary
    add_stored_moods_to_local_moods()
    initialize_moods()
    app.run()
