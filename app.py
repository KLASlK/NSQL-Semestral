from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['socialApp']
users_collection = db['users']


# Home
@app.route('/')
def index():
    my_friends = list(users_collection.find({"is_friend": True}))

    for user in my_friends:
        friend_names = []
        if user.get('friends'):
            for friend_id in user['friends']:
                friend = users_collection.find_one({'_id': ObjectId(friend_id)})
                if friend:
                    friend_names.append(friend['username'])
        user['friend_names'] = friend_names

    return render_template('index.html', users=my_friends)


# Create
@app.route('/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        is_friend = request.form.get('is_friend')

        if is_friend:
            is_friend = True
        else:
            is_friend = False

        if username and email:
            new_user = {
                'username': username, 
                'email': email, 
                'is_friend': is_friend,
                'friends': []
            }
            new_user_id = users_collection.insert_one(new_user).inserted_id

            selected_friends = request.form.getlist('friends')

            for friend_id in selected_friends:
                friend = users_collection.find_one({'_id': ObjectId(friend_id)})

                if friend:
                    users_collection.update_one(
                        {'_id': ObjectId(friend['_id'])},
                        {'$addToSet': {'friends': new_user_id}}
                    )
                    users_collection.update_one(
                        {'_id': new_user_id},
                        {'$addToSet': {'friends': ObjectId(friend['_id'])}}
                    )

        return redirect(url_for('index'))

    users = list(users_collection.find())
    return render_template('add.html', users=users)


# Read
@app.route('/users', methods=['GET'])
def user_list():
    search_query = request.args.get('search', '')
    if search_query:
        users = list(users_collection.find({'username': {'$regex': search_query, '$options': 'i'}}))
    else:
        users = list(users_collection.find())
    
    for user in users:
        friend_names = []
        if user.get('friends'):
            for friend_id in user['friends']:
                friend = users_collection.find_one({'_id': ObjectId(friend_id)})
                if friend:
                    friend_names.append(friend['username'])
        user['friend_names'] = friend_names

    return render_template('index.html', users=users)


# Update
@app.route('/edit/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    # Populate the friend names for the user
    friend_names = []
    if user.get('friends'):
        for friend_id in user['friends']:
            friend = users_collection.find_one({'_id': ObjectId(friend_id)})
            if friend:
                friend_names.append(friend['username'])
    user['friend_names'] = friend_names  # Add the friend names list to the user data

    # Fetch all users to show potential friends for adding
    users = list(users_collection.find())

    if request.method == 'POST':
        new_username = request.form.get('username')
        new_email = request.form.get('email')
        new_is_friend = request.form.get('is_friend')
        if new_is_friend:
            new_is_friend = True
        else:
            new_is_friend = False

        if new_username and new_email:
            # Update user data
            users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'username': new_username, 'email': new_email, 'is_friend': new_is_friend}}
            )

            # Handle removing friends
            remove_friends = request.form.getlist('remove_friends')
            if remove_friends:
                for friend_username in remove_friends:
                    # Find the friend by username
                    friend = users_collection.find_one({'username': friend_username})
                    if friend:
                        # Remove the user from the friend's friend list
                        users_collection.update_one(
                            {'_id': friend['_id']},
                            {'$pull': {'friends': ObjectId(user_id)}}
                        )
                        # Remove the friend from the user's friend list
                        users_collection.update_one(
                            {'_id': ObjectId(user_id)},
                            {'$pull': {'friends': ObjectId(friend['_id'])}}
                        )

            # Handle adding friends
            add_friends = request.form.getlist('add_friends')
            if add_friends:
                for friend_id in add_friends:
                    # Find the friend by ID
                    friend = users_collection.find_one({'_id': ObjectId(friend_id)})
                    if friend:
                        # Add the user to the friend's friend list
                        users_collection.update_one(
                            {'_id': friend['_id']},
                            {'$addToSet': {'friends': ObjectId(user_id)}}
                        )
                        # Add the friend to the user's friend list
                        users_collection.update_one(
                            {'_id': ObjectId(user_id)},
                            {'$addToSet': {'friends': ObjectId(friend['_id'])}}
                        )

        return redirect(url_for('index'))

    return render_template('edit.html', user=user, users=users)


# Delete
@app.route('/delete/<user_id>', methods=['POST'])
def delete_user(user_id):
    users_collection.delete_one({'_id': ObjectId(user_id)})
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
