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

db = SQLAlchemy(app)
auth = HTTPBasicAuth()

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
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
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
    args = moodParser.parse_args()
    mood = args['mood']
    if mood is None:
        return jsonify({'message': 'No mood entered'}), 400
    else: 
        now = datetime.now()
        if g.user.timestamp != None:
            if more_than_24_hours_apart(g.user.timestamp, now):
                g.user.streak = 1
            elif next_day(g.user.timestamp, now):
                g.user.streak += 1
        else:
            g.user.streak = 1

        g.user.timestamp = now
        moods[g.user.id].append(mood)
        write_local_moods_back_to_stored_moods()
        print("Moods: " + str(moods))
        return jsonify({'mood': mood})

def more_than_24_hours_apart(datetime1, datetime2):
    return (datetime2 - datetime1).total_seconds() > 86400

def next_day(datetime1, datetime2):
    return (datetime2.day - datetime1.day) == 1


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)
    if User.query.filter_by(username=username).first() is not None:
        abort(400)
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    moods[user.id] = []
    return (jsonify({'username':user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})

@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username, 'streak': user.streak, 'timestamp': user.timestamp, 'moods': moods})

@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})

def initialize_moods():
    users = User.query.all()
    for user in users:
        if user.id not in moods:
            moods[user.id] = []
    print("Moods: " + str(moods))

def write_local_moods_back_to_stored_moods():
    with open('moods.csv', 'w') as csv_file:
        csv_writer = writer(csv_file)
        users = User.query.all()
        print("Final Moods: " + str(moods))
        for user in users:
            row = moods[user.id]
            print(row)
            csv_writer.writerow(row)

if __name__ == "__main__":
    if not os.path.exists('db.sqlite'):
        db.create_all()
    if not os.path.exists('moods.csv'):
        fp = open('moods.csv', 'x')
        fp.close()

    add_stored_moods_to_local_moods()
    initialize_moods()
    print(moods)
    app.run(debug=True)
