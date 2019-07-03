from app import app
import unittest
import random
import string

def randomString(stringLength=10):
	"""Generate a random string of fixed length """
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(stringLength))


class FlaskappTests(unittest.TestCase):
	
	def setUp(self):
		#create a test client
		self.app = app.test_client()

		#send exceptions to the test client
		self.app.testing = True

	def test_users_status_code(self):
		#send HTTP GET to the app
		result = self.app.get('/api/v1/users')

		self.assertEqual(result.status_code, 200)

	def test_tweets_status_code(self):
		result = self.app.get('/api/v2/tweets')
		self.assertEqual(result.status_code, 200)


	def test_add_users_status_code(self):
		username = randomString()
		email = username + '@gmail.com'
		result = self.app.post('/api/v1/users', 
					data='{"username": "'+ username +'", "email":"' + email + '", "password": "p123"}',
					content_type='application/json')
		print(result)
		self.assertEquals(result.status_code, 201)

	def test_updusers_status_code(self):
		result = self.app.put('/api/v1/users/1234', 
			data='{"password": "123"}', 
			content_type='application/json')
		self.assertEquals(result.status_code, 200)

	def test_addtweets_status_code(self):
		result = self.app.post('/api/v2/tweets', 
				data='{"username": "bobj", "body":"test tweet"}',   
				content_type='application/json')
		self.assertEqual(result.status_code, 201)

	def test_delusers_status_code(self):
		
		self.app.post('/api/v1/users', 
					data='{"username": "testrunner", "email":"testrunner@test.com", "password": "p123"}',
					content_type='application/json')

		result = self.app.delete('/api/v1/users', 
			data='{"username":"testrunner"}', 
			content_type='application/json')

		self.assertEquals(result.status_code, 200) 