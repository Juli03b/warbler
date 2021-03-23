"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
import psycopg2

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):

    def setUp(self):
        """Create test client, add sample data."""
        db.session.rollback()
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=None
        )

        db.session.add(u)
        db.session.commit()

        self.u = u
        self.u_pass = "HASHED_PASSWORD"

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work, and are all attributes correct?"""

        u = User(
            email="test@test2.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertIsInstance(u.id, int)
        self.assertEqual(u.username, "testuser2")
        self.assertEqual(str(u), repr(u))
        self.assertGreater(len(u.image_url), 1)
        self.assertEqual(u.bio, None)
        self.assertEqual(u.location, None)
        self.assertGreater(len(u.header_image_url), 1)
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    

    def test_user_authentication(self):
        """Does user authentication return user when password is correct, 
        and False when password or username are incorrect?"""

        user = User.authenticate(self.u.username, self.u_pass)
        wrong_pass = User.authenticate(self.u.username, 'he110')
        wrong_user = User.authenticate('h1', self.u_pass)

        self.assertEqual(user, self.u)
        self.assertEqual(wrong_pass, False)
        self.assertEqual(wrong_user, False)

    def test_create_user(self):
        """Does user creation fail if username or email is taken, 
        or if required fields are empty"""

        user = User(username='tset', password='SSAPTSET', email='liametset@tset.com', image_url='')
        db.session.add(user)
        db.session.commit()
        
        duplicate_username = User(username='tset', password='SSAPTSET', email='liametset@tset.com2', image_url='')
        duplicate_email = User(username='tset2', password='SSAPTSET', email='liametset@tset.com', image_url='')
        duplicate_user = User(username='tset', password='SSAPTSET', email='liametset@tset.com', image_url='')
        null_username = User(username=None, password='SSAPTSET', email='liametset@tset.com', image_url='')
        null_email = User(username='tset', password='SSAPTSET', email=None, image_url='')

        self.assertIsInstance(user, User)
        
        with self.assertRaises(Exception) as err:
            db.session.add(duplicate_username)
            db.session.commit()

        with self.assertRaises(Exception) as err:
            db.session.add(duplicate_email)
            db.session.commit()

        with self.assertRaises(Exception) as err:
            db.session.add(duplicate_user)
            db.session.commit()

        with self.assertRaises(Exception) as err:
            db.session.add(null_entry)
            db.session.commit()

        with self.assertRaises(Exception) as err:
            db.session.add(null_email)
            db.session.commit()

    def test_user_following_and_followed_by(self):
        """Does following work, and does is_following and is_followed_by methods work?
        Return True when user is following/followed by, return False if not.
        """

        user = User(username='tset', password='SSAPTSET', email='liametset@tset.com', image_url='')
        user.following.append(self.u)

        db.session.add(user)
        db.session.commit()
                
        self.assertIn(self.u, user.following)

        self.assertTrue(self.u.is_followed_by(user))
        self.assertTrue(user.is_following(self.u))

        self.assertFalse(self.u.is_following(user))
        self.assertFalse(user.is_followed_by(self.u))
