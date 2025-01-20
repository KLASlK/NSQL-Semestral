from pymongo import MongoClient
from bson import ObjectId
import random

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['socialApp']
users_collection = db['users']

# List of all user IDs
all_ids = [
    ObjectId('678d481027437a3d09aad43e'),
    ObjectId('678d48c527437a3d09aad440'),
    ObjectId('678d48d627437a3d09aad441'),
    ObjectId('678d48fb27437a3d09aad442'),
    ObjectId('678d493827437a3d09aad443'),
    ObjectId('678d496527437a3d09aad444'),
    ObjectId('678d49c327437a3d09aad445'),
    ObjectId('678d4a2327437a3d09aad446'),
    ObjectId('678d4a7727437a3d09aad447'),
    ObjectId('678d4abd27437a3d09aad448'),
    ObjectId('678d4bec27437a3d09aad44a'),
    ObjectId('678d4c1127437a3d09aad44b'),
    ObjectId('678d91c8833833ceda709f77')
]

# Initialize empty friends arrays for all users
users_collection.update_many({}, {'$set': {'friends': []}})

# Function to add symmetric friendship
def add_symmetric_friendship(user_id1, user_id2):
    # Add user_id2 to user_id1's friends if not already there
    users_collection.update_one(
        {'_id': user_id1},
        {'$addToSet': {'friends': user_id2}}
    )
    # Add user_id1 to user_id2's friends if not already there
    users_collection.update_one(
        {'_id': user_id2},
        {'$addToSet': {'friends': user_id1}}
    )

# Randomly create symmetric friendships
for user_id in all_ids:
    # Choose random friends for this user
    num_friends = random.randint(0, 5)  # Choose up to 5 friends
    potential_friends = [uid for uid in all_ids if uid != user_id]
    friends = random.sample(potential_friends, num_friends)

    # Ensure symmetry by adding both directions
    for friend_id in friends:
        add_symmetric_friendship(user_id, friend_id)

print("Symmetric friendships assigned successfully!")
