from flask import Flask, jsonify, request, send_file
from flask_cors import CORS, cross_origin
from models.user import User
from models.profile import Profile
import json
from io import BytesIO
from bson import ObjectId
from pymongo import MongoClient
from gridfs import GridFS


client = MongoClient('mongodb://mongo:27017/')
fs = GridFS(client['tp'])


app = Flask(__name__)
CORS(app, resources=r'/api/*')

# ===============================================
#                   GAMES ENDPOINTS
# ===============================================

# GET IMAGE FOR THE GAME
@app.route('/api/image/<id>', methods=['GET'])
@cross_origin()
def get_img(id):
    file = fs.get(ObjectId(id))
    img_stream = BytesIO(file.read())
    return send_file(img_stream, mimetype='image/jpeg')

# GETM GAMES LIST WITH INFORMATION
@app.route('/api/games', methods=['GET'])
def get_data():
    data = list(client['tp']['games'].find())
    for game in data:
        game['_id'] = str(game['_id'])
        # Send the id back and have front end get it from another endpoint
        game['game_img'] = str(game['game_img'])
    return jsonify(data), 200

#ADD A GAME
@app.route('/api/game', methods=['POST'])
def add_game():
    name = request.form.get('name')
    game_info = {
        'name': name
    }
    image_file = request.files['image']
    file_id = fs.put(image_file)
    game_info['game_img'] = file_id
    id = client['tp']['games'].insert_one(game_info).inserted_id
    if request.form.get('user_id'):
        
        profile = client['tp']['profiles'].find_one({'user_id': request.form.get('user_id')})
        print(profile)
        print(profile['games'])
        games = profile['games']
        games.append(str(id))
        games = list(set(games))
        print(games)
        client['tp']['profiles'].find_one_and_update({'user_id': profile['user_id']}, {'$set': {"games": games}})
    return 'ok', 200


# ===============================================
#                   USER ENDPOINTS
# ===============================================

# REGIST A USER
@app.route('/api/sign_up', methods=['POST'])
@cross_origin()
def sign_up():
    data = request.get_json()
    username = data.get('username')
    name = data.get('name')
    password = data.get('password')
    if username and name and password:
        user_id = User.save_user(
            username=username,
            password=password,
            name=name,
            database=client['tp']
        )
        if user_id:
            return jsonify({'userId': user_id}), 200
        else:
            return 'some error', 400
    elif not username:
        return 'missing username', 400
    elif not password:
        return 'missing password', 400
    else:
        return 'missing name', 400
    

# MOCK A LOGIN 
@app.route('/api/login', methods=['POST'])
@cross_origin()
def login():
    user_info = request.get_json()
    if user_info.get('username') and user_info.get('password'):
        username = user_info['username']
        password = user_info['password']
        db = client['tp']
        users = db['users']
        user = users.find_one({'username': username})
        if user:
            if user['password'] != password:
                return jsonify(message="Wrong password"), 403
            users.update_one({'username': username}, {'$set': {'online': True}})
            response = {
                'userId': str(user['_id']),
                'msg': 'Successful'
            }
            return jsonify(response), 200
        else:
            return jsonify(message="User does not exist"), 404
    else:
        return jsonify(message="missing password or username"), 404
    
    
# GET THE PROFILE FOR THE USER
@app.route('/api/profile/<user_id>', methods=['GET'])
@cross_origin()
def profile_get(user_id):
    db = client['tp']
    data = User.profile(db, user_id)
    data.pop('_id')
    if data:
        return jsonify(data), 200
    else:
        return  jsonify(message="'Profile does not exist'"), 404


# ADD GAME TO THIS PROFILE
@app.route('/api/profile/<user_id>/games', methods=['POST'])
@cross_origin()
def profile_add_game_to_profile(user_id):
    db = client['tp']
    data = request.get_json()
    Profile.add_game_to_profile(db, data['gameId'], user_id)
    return 'ok', 200

# GET THE GAMES IN THE PROFILE
@app.route('/api/profile/<user_id>/games', methods=['GET'])
def get_games_from_profile(user_id):
    try:
        user_profile = db['profiles'].find_one({'user_id': ObjectId(user_id)})
        if not user_profile:
            return jsonify(message="Profile not found"), 404

        games = user_profile.get('games', [])
        games_info = db['games'].find({'_id': {'$in': [ObjectId(game_id) for game_id in games]}})

        games_data = []
        for game in games_info:
            # Assuming 'image_id' holds the GridFS file reference in the game document
            game_data = {
                'name': game['name'],
                'id': str(game['_id']),
                'image_id': str(game.get('image_id', '')),  # Make sure to store image reference correctly
                # Assume ratings is a dictionary with user_id keys and rating values
                'rating': game.get('ratings', {}).get(str(user_id), 'Not Rated')
            }
            games_data.append(game_data)

        return jsonify(games_data), 200
    except Exception as e:
        return jsonify(message=str(e)), 500




# GET THE GAMES IN WISH LIST
@app.route('/api/profile/<user_id>/wish', methods=['POST'])
@cross_origin()
def profile_add_game_to_wish(user_id):
    db = client['tp']
    data = request.get_json()
    Profile.add_game_to_wish_list(db, data['gameId'], user_id)
    return 'ok', 200


@app.route('/api/games/<user_id>', methods=['POST'])
@cross_origin()
def rate_game():
    data = request.get_json()
    game_id = data.get('gameId')
    score = data.get('score')
    
    if not game_id or score is None:
        return jsonify({'message': 'Missing gameId or score'}), 400
    
    db = client['tp']
    games_collection = db['games']
    
    # Here you need to define how you want to store the rating. This is just an example:
    result = games_collection.update_one(
        {'_id': ObjectId(game_id)},
        {'$set': {'rating': score}}
    )
    
    if result.matched_count:
        return jsonify({'message': 'Rating updated successfully'}), 200
    else:
        return jsonify({'message': 'Game not found'}), 404

    # ===============================================
#                   ADMIN ENDPOINTS
# ===============================================
# GET ALL USERS
@app.route('/api/admin/users', methods=['GET'])
@cross_origin()
def admin_get_users():
    db = client['tp']
    users_collection = db['users']

    try:
       
        users = list(users_collection.find({}))  
        for user in users:
            user['_id'] = str(user['_id'])  

        return jsonify(users), 200

    except Exception as e:
        return jsonify(message=str(e)), 500
# DELETE A USER
@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@cross_origin()
def admin_delete_user(user_id):
    db = client['tp']
    users_collection = db['users']

    result = users_collection.delete_one({'_id': ObjectId(user_id)})

    if result.deleted_count:
        return jsonify(message="User deleted successfully"), 200
    else:
        return jsonify(message="User not found"), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
