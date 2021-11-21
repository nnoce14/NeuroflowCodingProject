import os, time
from csv import reader
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
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

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

moodParser = reqparse.RequestParser()
moodParser.add_argument('mood', type=str, help='No mood entered...')

# Endpoints
@app.route('/api/mood', methods=['GET'])
@auth.login_required
def get_moods():
    return jsonify({'moods': get_moods_for_user(g.user)})

def get_moods_for_user(user):
    if user is None:
        return "None"
    else:
        return moods[user.id]

def add_stored_moods_to_local_moods():
    with open('moods.csv', 'r') as csv_file:
        csv_reader = reader(csv_file)
        userID = 1;
        for row in csv_reader:
            row = rowsplit(",")
            moods[userID] = [row] if type(row) == str else row
            print(moods[userID])
            userID += 1

@app.route('/api/mood', methods=['POST'])
@auth.login_required
def add_mood():
    args = moodParser.parse_args()
    mood = args['mood']
    if mood is None:
        return jsonify({'message': 'No mood entered'}), 400
    else: 
        moods[g.user.id].append(mood)
        return jsonify({'mood': mood})


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
    return (jsonify({'username':user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})

@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

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
