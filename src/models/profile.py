from bson import ObjectId

class Profile:
    @staticmethod
    def save_profile(base_info, database):
        collection = database['profiles']
        # This should not happen but is a security measure
        profile = collection.find_one(
            {
                'username': base_info['username']
            }
        )
        if profile:
            return False
        collection.insert_one(base_info)
        return True
    
    @staticmethod
    def add_game_to_profile(database, game_id, profile_id):
        database['profiles'].update_one(
            {
                'user_id': profile_id
            },
            {
                '$push': {
                    'games': game_id
                }
            }
        )
        
    @staticmethod
    def get_games(database, profile_id):
      profile = database['profiles'].find_one({'user_id': ObjectId(profile_id)})
      if profile and 'games' in profile:
        game_ids = [ObjectId(game['game_id']) for game in profile['games']]
        games = list(database['games'].find({'_id': {'$in': game_ids}}))
        
        # Include ratings in the game data returned
        for game in games:
            # Extract the game id for comparison
            game_id = game['_id']
            # Find the game in the profile to get the rating
            profile_game = next((item for item in profile['games'] if item['game_id'] == str(game_id)), None)
            game['rating'] = profile_game.get('rating') if profile_game else 'Not Rated'
            game['_id'] = str(game['_id'])
            game['game_img'] = str(game['game_img']) if 'game_img' in game else 'No Image'
        return games
        return []

            
        
    @staticmethod
    def add_game_to_wish_list(database, game_id, profile_id):
        database['profiles'].update_one(
            {
                'user_id': profile_id
            },
            {
                '$push': {
                    'wish_list': game_id
                }
            }
        )

    @staticmethod
    def rate_game(database, game_id, profile_id, rating):
        # Ensure the rating is an integer or float within expected bounds
        rating = max(0, min(rating, 5))  # Assuming a rating scale of 0 to 5

        # Update or add a rating for a game in the user's profile
        result = database['profiles'].update_one(
            {'user_id': ObjectId(profile_id), 'games.game_id': game_id},
            {'$set': {'games.$.rating': rating}}
        )
        
        # If the game is not in the list, push a new entry
        if result.matched_count == 0:
            database['profiles'].update_one(
                {'user_id': ObjectId(profile_id)},
                {'$push': {'games': {'game_id': game_id, 'rating': rating}}}
            ) 
        