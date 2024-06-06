from .profile import Profile
from bson import ObjectId

class User:
    @staticmethod
    def save_user(username, password, name, database):
        collection = database['users']
        user = collection.find_one({'username': username})
        if user:
            return False
        user = collection.insert_one(
            {
                'username': username,
                'password': password,
                'name': name
            }
        )
        user_id = str(user.inserted_id)
        base_profile = {
            'username': username,
            'user_id': str(user.inserted_id),
            'name': name,
            'games': [],
            'wish_list': []
        }
        Profile.save_profile(base_info=base_profile, database=database)
        return user_id
    
    @staticmethod
    def get_games(db, profile, collection):
       
        print(profile[collection])
        ids = []
        for id in profile[collection]:
            ids.append(ObjectId(id))
        games = db['games'].find({'_id': {'$in': ids}})
        new_format = []
        for game in games:
            print(game)
            new_format.append(
                {
                    '_id': str(game['_id']),
                    'name': game['name']
                }
            )
        return new_format
    
    @staticmethod
    def profile(database, id):
        profile = database['profiles'].find_one({'user_id': id})
        profile['games'] = User.get_games(database, profile, 'games')
        profile['wish_list'] = User.get_games(database, profile, 'wish_list')
        print(profile, '\n\n')
        return profile
    
    @property
    def password(self):
        return self._password
    
    @property
    def name(self):
        return self._name