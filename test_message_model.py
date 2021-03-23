import os
from unittest import TestCase

from models import db, User, Message, Follows, datetime
import psycopg2

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

class MessageModelTestCase(TestCase):

    def setUp(self):
        """Setup user and message"""

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
        
        msg = Message(text="h1", user_id=u.id)

        u.messages.append(msg)
        db.session.commit()

        self.u = u

    def test_message_model(self):
        """Test all message attributes"""

        [msg] = self.u.messages
        
        self.assertEqual(msg.text, "h1")
        self.assertIsInstance(msg.timestamp, datetime)
        self.assertIsInstance(msg.user_id, int)
        self.assertIs(msg.user, self.u)
    
    def test_create_message(self):
        """Test that submitting null values causes an exception"""
        u = self.u
        msg = Message(text='h3110', user_id=u.id)

        u.messages.append(msg)
        db.session.commit()

        null_text = Message(text=None, user_id=u.id)
        null_user_id = Message(text='h3110', user_id=None)
        null_msg = Message(text=None, user_id=None)

        self.assertIsInstance(msg, Message)

        with self.assertRaises(Exception) as err:
            db.session.add(null_text)
            db.session.commit()

        with self.assertRaises(Exception) as err:
            db.session.add(null_user_id)
            db.session.commit()

        with self.assertRaises(Exception) as err:
            db.session.add(null_msg)
            db.session.commit()

