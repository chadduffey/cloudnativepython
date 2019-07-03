from app import app
import unittest

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

