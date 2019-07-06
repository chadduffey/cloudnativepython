from flask import Flask, jsonify, make_response, request, abort, render_template
from flask_cors import CORS, cross_origin

import json
import sqlite3
import time

app = Flask(__name__)

@app.errorhandler(404)
def resource_not_found(error):
	return make_response(jsonify({'error':'Resource not found'}), 404)

@app.errorhandler(400)
def invalid_request(error):
	return make_response(jsonify({'error': 'Bad request'}), 400)

@app.errorhandler(409)
def invalid_request(error):
	return make_response(jsonify({'error': 'Object Exists'}), 400)

def list_users():
	conn = sqlite3.connect('mydb.db')
	print("Opened database successfully")
	api_list=[]
	cursor = conn.execute("SELECT username, full_name, emailid, password, id from users")
	for row in cursor:
		a_dict = {}
		a_dict['username'] = row[0]
		a_dict['name'] = row[1]
		a_dict['email'] = row[2]
		a_dict['password'] = row[3]
		a_dict['id'] = row[4]
		api_list.append(a_dict)
	conn.close()
	return jsonify({'user_list':api_list})

def list_user(user_id):
	conn = sqlite3.connect('mydb.db')
	print("Opened database successfully")
	cursor = conn.cursor()
	cursor = conn.execute("SELECT * from users where id=?",(user_id,))
	data = cursor.fetchall()
	user = {}
	if len(data) != 0:
		user['username'] = data[0][0]
		user['name'] = data[0][1]
		user['email'] = data[0][2]
		user['password'] = data[0][3]
		user['id'] = data[0][4]
	conn.close()
	return jsonify(user)

def add_user(new_user):
	conn = sqlite3.connect('mydb.db')
	print("Opened database successfully")
	a_dict={}
	cursor = conn.cursor()
	cursor.execute(
		"SELECT * from users where username=? or emailid=?",(new_user['username'],new_user['email']))
	data = cursor.fetchall()
	if len(data) != 0:
		abort(409)
	else:
		cursor.execute(
			"insert into users (username, emailid, password, full_name) values(?,?,?,?)",
			(new_user['username'],new_user['email'], new_user['password'], new_user['name']))
		conn.commit()
		print("Success")
	conn.close()
	return 201

def del_user(del_user):
	conn = sqlite3.connect('mydb.db')
	print("Opened database successfully")
	cursor = conn.cursor()
	cursor.execute("SELECT * from users where username=?", (del_user,))
	data = cursor.fetchall()
	print("Data", data)
	if len(data) == 0:
		abort(404)
	else:
		cursor.execute("delete from users where username==?", (del_user,))
		conn.commit()
	return "Success"

def upd_user(user):
	conn = sqlite3.connect("mydb.db")
	print("Opened database successfully")
	cursor=conn.cursor()
	cursor.execute("SELECT * from users where id=?", (user['id'],))
	data = cursor.fetchall()
	print(data)
	if len(data) == 0:
		abort(404)
	else:
		key_list=user.keys()
		for i in key_list:
			if i != "id":
				print(user, i)
				cursor.execute("""UPDATE users SET {0} = ? WHERE id = ?""".format(i), 
					(user[i], user['id']))
				conn.commit()
	return "Success"

def list_tweets():
	print("list_tweets")
	conn = sqlite3.connect('mydb.db')
	print("Database opened successfully")
	api_list=[]
	cursor = conn.execute("SELECT username, body, tweet_time, id from tweets")
	data = cursor.fetchall()
	if data != 0:
		for row in data:
			tweets = {}
			tweets['Tweet by'] = row[0]
			tweets['Body'] = row[1]
			tweets['Timestamp'] = row[2]
			tweets['Id'] = row[3]
			api_list.append(tweets)
	else:
		conn.close()
		return api_list
	print(api_list)
	conn.close()
	return jsonify({'tweets_list': api_list})

def add_tweet(new_tweets):
	conn = sqlite3.connect('mydb.db')
	print ("Opened database successfully");
	cursor=conn.cursor()
	cursor.execute("SELECT * from users where username=? ",   (new_tweets['username'],))
	data = cursor.fetchall()

	if len(data) == 0:
		abort(404)
	else:
		cursor.execute("INSERT into tweets (username, body, tweet_time) values(?,?,?)",
			(new_tweets['username'],new_tweets['body'], new_tweets['created_at']))
		conn.commit()
		return "Success"

def list_tweet(user_id):
	print(user_id)
	conn = sqlite3.connect('mydb.db')
	print("Opened successfully")
	api_list = []
	cursor = conn.cursor()
	cursor.execute("SELECT * from tweets where id=?", (user_id,))
	data = cursor.fetchall()
	print(data)
	if len(data) == 0:
		abort(404)
	else:
		user = {}
		user['id'] = data[0][0]
		user['username'] = data[0][1]
		user['body'] = data[0][2]
		user['tweet_time'] = data[0][3]
		conn.close()
		return jsonify(user)

@app.route("/api/v1/info")
def home_index():
	conn = sqlite3.connect('mydb.db')
	print("Opened database successfully")
	api_list=[]
	cursor = conn.execute("SELECT buildtime, version, methods, links from apirelease")
	for row in cursor:
		a_dict = {}
		a_dict['version'] = row[0]
		a_dict['buildtime'] = row[1]
		a_dict['methods'] = row[2]
		a_dict['links'] = row[3]
		api_list.append(a_dict)
	conn.close()
	return jsonify({'api_version': api_list}), 200

@app.route("/api/v1/users", methods=['GET'])
def get_users():
	return list_users()

@app.route("/api/v1/users/<int:user_id>", methods=['GET'])
def get_user(user_id):
	return list_user(user_id)

@app.route("/api/v1/users", methods=['POST'])
def create_user():
	if not request.json or not 'username' in request.json \
			or not 'email' in request.json or not 'password' in request.json:
		abort(400)
	user = {
		'username' : request.json['username'],
		'email' : request.json['email'],
		'name' : request.json.get('name',""),
		'password' : request.json['password']
	}
	return jsonify({'status': add_user(user)}), 201


@app.route("/api/v1/users", methods=['DELETE'])
def delete_user():
	if not request.json or not 'username' in request.json:
		abort(400)
	user=request.json['username']
	return jsonify({'status': del_user(user)}), 200

@app.route("/api/v1/users/<int:user_id>", methods=['PUT'])
def update_user(user_id):
	user = {}
	if not request.json:
		abort(400)
	user['id'] = user_id
	key_list = request.json.keys()
	for i in key_list:
		user[i] = request.json[i]
	print(user)
	return jsonify({'status': upd_user(user)}), 200

@app.route('/api/v2/tweets', methods=['GET'])
def get_tweets():
	return list_tweets()


@app.route('/api/v2/tweets', methods=['POST'])
def add_tweets():
	user_tweet = {}
	if not request.json or not 'username' in request.json or not 'body' in request.json:
		abort(400)
	user_tweet['username'] = request.json['username']
	user_tweet['body'] = request.json['body']
	user_tweet['created_at'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
	print(user_tweet)
	return jsonify({'status': add_tweet(user_tweet)}), 201


@app.route('/api/v2/tweets/<int:id>', methods=['GET'])
def get_tweet(id):
	return list_tweet(id)

@app.route('/adduser')
def adduser():
	return render_template('adduser.html')

@app.route('/addtweets')
def addtweetjs():
	render_template('addtweets.html')


if __name__ == "__main__":
	
	CORS(app)

	app.run(host='0.0.0.0', port=5000, debug=True)
