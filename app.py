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
    friends = list(users_collection.find({"is_friend": True}))
    return render_template('index.html', users=friends)

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
            users_collection.insert_one({'username': username, 'email': email, 'is_friend' : is_friend})
        return redirect(url_for('index'))
    return render_template('add.html')

# Read
@app.route('/users')
def user_list():
    users = list(users_collection.find())
    return render_template('index.html', users=users)

# Update
@app.route('/edit/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_email = request.form.get('email')
        new_is_friend = request.form.get('is_friend')
        if new_is_friend:
            new_is_friend = True
        else:
            new_is_friend = False

        if new_username and new_email:
            users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'username': new_username, 'email': new_email, 'is_friend': new_is_friend}}
            )
        return redirect(url_for('index'))
    return render_template('edit.html', user=user)

# Delete
@app.route('/delete/<user_id>', methods=['POST'])
def delete_user(user_id):
    users_collection.delete_one({'_id': ObjectId(user_id)})
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
