from flask import Flask, render_template, request, jsonify, redirect, session
from flask import abort
from flask_cors import CORS, cross_origin
from flask import make_response, url_for

from pymongo import MongoClient
from time import gmtime, strftime

import json 
import random
import sqlite3
import requests

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = '#&*^%$@(*GHere'
CORS(app)

connection = MongoClient("mongodb://localhost:27017/")


def create_mongodatabase():
	try:
		dbnames = connection.database_names()
		if 'cloud_native' not in dbnames:
			db = connection.cloud_native.users
			db_tweets = connection.cloud_native.tweets
			db_api = connection.cloud_native.apirelease
			
			db.insert({
				"email": "duff@google.com",
				"id": 33,
				"name": "C Duff",
				"password": "pass",
				"username": "duff"
			})
			
			db_tweets.insert({
				"body": "Most interesting things",
				"id": 18,
				"timestamp": "2019-07-07T06:39:40Z",
				"tweetedby": "duff"
			})
			
			db_api.insert( {
				"buildtime": "2017-01-01 10:00:00",
				"links": "/api/v1/users",
				"methods": "get, post, put, delete",
				"version": "v1"
			})
			
			db_api.insert( {
				"buildtime": "2017-02-11 10:00:00",
				"links": "api/v2/tweets",
				"methods": "get, post",
				"version": "2017-01-10 10:00:00"
			})

			print("Database initialized")
		else:
			print("Database was already initialized")
	except:
		print("Database creation failed")


def list_users():
	api_list=[]
	db = connection.cloud_native.users
	for row in db.find():
		api_list.append(str(row))
	return jsonify({'user_list': api_list})


def list_user(user_id):
	api_list=[]
	db = connection.cloud_native.users
	for i in db.find({'id':user_id}):
		api_list.append(str(i))

	if api_list == []:
		return abort(404)

	return jsonify({'user_details':api_list})


def list_tweet(user_id):
	db = connection.cloud_native.tweets
	api_list = []
	tweet = db.find({'id':user_id})
	for i in tweet:
		api_list.append(str(i))
	if api_list == []:
		return abort(404)
	return jsonify({'tweet': api_list})


def add_user(new_user):
	api_list=[]
	print(new_user)
	db = connection.cloud_native.users
	user = db.find({'$or':[{"username":new_user['username']},
					{"email": new_user['email']}  ]})
	for i in user:
		print(str(i))
		api_list.append(str(i))

	if api_list == []:
		db.insert(new_user)
		return "Success"
	else:
		return abort(409)


def del_user(del_user):
	db = connection.cloud_native.users
	api_list = []
	for i in db.find({'username':del_user}):
		api_list.append(str(i))
	if api_list == []:
		return abort(404)
	else:
	   db.remove({'username':del_user})
	   return "Success"


def list_tweets():
	api_list = []
	db = connection.cloud_native.tweets
	for row in db.find():
		api_list.append(str(row))
	return jsonify({'tweets_list':api_list})


def add_tweet(new_tweet):
	api_list = []
	print(new_tweet)
	db_user = connection.cloud_native.users
	db_tweet = connection.cloud_native.tweets
	user = db_user.find({'username':new_tweet['tweetedby']})
	for i in user:
		api_list.append(str(i))
	if api_list == []:
		return abort(404)
	else:
		db_tweet.insert(new_tweet)
		return "Success"


def upd_user(user):
	api_list = []
	print(user)
	db_user = connection.cloud_native.users
	users = db_user.find_one({"id":user['id']})
	for i in users:
		api_list.append(str(i))
	if api_list == []:
		return abort(409)
	else:
		db_user.update({'id':user['id']}, {'$set': user}, upsert=False)
	return "Success"


def sumSessionCounter():
	try:
		session['counter'] += 1
	except KeyError:
		session['counter'] = 1


@app.route('/')
def main():
	sumSessionCounter()
	return render_template('main.html')


@app.route('/addname')
def addname():
	sumSessionCounter()
	if request.args.get('yourname'):
		session['name'] = request.args.get('yourname')
		# And then redirect the user to the main page
		return redirect(url_for('main'))
	else:
		# If no name has been sent, show the form
		return render_template('addname.html', session=session)


@app.route('/clear')
def clearsession():
	# Clear the session
	session.clear()
	# Redirect the user to the main page
	return redirect(url_for('main'))


@app.route('/adduser')
def adduser():
	return render_template('adduser.html')


@app.route('/addtweets')
def addtweetjs():
	return render_template('addtweets.html')


@app.route("/api/v1/info")
def home_index():
	api_list=[]
	db = connection.cloud_native.apirelease
	for row in db.find():
		api_list.append(str(row))
	return jsonify({'api_version': api_list}), 200


@app.route('/api/v1/users', methods=['GET'])
def get_users():
	return list_users()


@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
	return list_user(user_id)


@app.route('/api/v1/users', methods=['POST'])
def create_user():
	if not request.json or not 'username' in request.json or not 'email' in request.json or not 'password' in request.json:
		abort(400)
	user = {
		'username': request.json['username'],
		'email': request.json['email'],
		'name': request.json.get('name',""),
		'password': request.json['password'],
		'id': random.randint(1,1000)
	}
	return jsonify({'status': add_user(user)}), 201


@app.route('/api/v1/users', methods=['DELETE'])
def delete_user():
	if not request.json or not 'username' in request.json:
		abort(400)
	user=request.json['username']
	return jsonify({'status': del_user(user)}), 200


@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
	user = {}
	user['id']=user_id
	key_list = request.json.keys()
	for i in key_list:
		user[i] = request.json[i]
	print (user)
	return jsonify({'status': upd_user(user)}), 200


@app.route('/api/v2/tweets', methods=['GET'])
def get_tweets():
	return list_tweets()


@app.route('/api/v2/tweets', methods=['POST'])
def add_tweets():

	user_tweet = {}
	if not request.json or not 'username' in request.json or not 'body' in request.json:
		abort(400)
	user_tweet['tweetedby'] = request.json['username']
	user_tweet['body'] = request.json['body']
	user_tweet['created_at']=strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())
	print (user_tweet)
	return  jsonify({'status': add_tweet(user_tweet)}), 201


@app.route('/api/v2/tweets/<int:id>', methods=['GET'])
def get_tweet(id):
	return list_tweet(id)


@app.errorhandler(404)
def resource_not_found(error):
	return make_response(jsonify({'error': 'Resource not found!'}), 404)


@app.errorhandler(409)
def user_found(error):
	return make_response(jsonify({'error': 'Conflict! Record exist'}), 409)


@app.errorhandler(400)
def invalid_request(error):
	return make_response(jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':
	create_mongodatabase()
	app.run(host='0.0.0.0', port=5000, debug=True)