from flask import Flask, request, make_response, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from functools import wraps
import jwt
import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisisthesecretkey'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = request.headers['Authorization']
        except:
            token = None
        if not token:
            return make_response({
                'message': 'Token is missing'
            }, 403)
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        except:
            return make_response({
                'message': 'Token is invalid'
            }, 403)
        return f(*args, **kwargs)
    return decorated

try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client.python_2
    print('Database connected')
except Exception as e:
    print('ERROR - Cannot connect to database')

@app.route('/login', methods = ['POST'])
def login():
    token = jwt.encode({
        'user': request.json['username'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    return make_response(jsonify({
        'token': token
    }), 200)

@app.route('/user', methods = ['GET'])
@token_required
def index():
    try:
        users = list(db.users.find())
        for user in users:
            user['_id'] = str(user['_id'])
        return make_response(jsonify({
            'message': 'user data has been loaded',
            'data': users
        }), 200)
    except Exception as e:
        return make_response(jsonify({
            'message': 'user data vailed to load',
            'error': str(e)
        }), 500)

@app.route('/user/show/<id>', methods = ['GET'])
def show(id):
    try:
        user = db.users.find_one({ '_id': ObjectId(id) })
        user['_id'] = str(user['_id'])
        return make_response(jsonify({
            'message': 'user data has been loaded',
            'data': user
        }), 200)

    except Exception as e:
        return make_response(jsonify({
            'message': 'user data vailed to load',
            'error': str(e)
        }), 500)


@app.route('/user/store', methods = ['POST'])
def store():
    try:
        req = {
            'name': request.json['name'],
            'email': request.json['email']
        }
        user_id = db.users.insert_one(req).inserted_id
        return make_response(jsonify({
            'message': 'user data has been saved',
            'user_id': str(user_id)
        }), 200)
    except Exception as e:
        return make_response(jsonify({
            'message': 'user data vailed to save',
            'error': str(e)
        }), 500)

@app.route('/user/update/<id>', methods = ['PUT'])
def update(id):
    try:
        req = {
            'name': request.json['name'],
            'email': request.json['email']
        }
        user = db.users.update_one({'_id': ObjectId(id)}, {'$set': req})
        if user.modified_count >= 1:
            return make_response(jsonify({
                'message': 'user data has been updated'
            }), 200)
        else:
            return make_response(
            jsonify({
                'message': 'user data is not updated'
            }), 200)
    except Exception as e:
        return make_response(jsonify({
            'message': 'user data vailed to update',
            'error': str(e)
        }), 500)

@app.route('/user/destroy/<id>', methods = ['DELETE'])
def destroy(id):
    try:
        user = db.users.delete_one({'_id': ObjectId(id)})
        if user.deleted_count >= 1:
            return make_response(jsonify({
                'message': 'user data has been deleted'
            }), 200)
        else:
            return make_response(jsonify({
                'message': 'user data is not deleted'
            }), 200)
    except Exception as e:
        return make_response(jsonify({
            'message': 'user data vailed to delete',
            'error': str(e)
        }), 500)
        
app.run()