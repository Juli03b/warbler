import os
from unittest import TestCase
from models import db, connect_db, Message, User, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):

    def setUp(self):
        
        db.session.rollback()
        Follows.query.delete()
        User.query.delete()
        Message.query.delete()
        
        self.client = app.test_client()

        self.test_user = User.signup('t3st', 'test@t3st.com', 't3stts3t', None)
        self.user_pass = 't3stts3t'
        
        self.test_user2 = User.signup('t3st2', 'test@t3st.com2', 't3stts3t', None)

        db.session.commit()

        self.user2_id = self.test_user2.id

    def test_list_users(self):
        """Test user list and user search"""

        with self.client as c:
            res = c.get('/users')
            html = res.get_data(as_text=True)

            # Test list all users  
            self.assertIn(self.test_user.username, html)

            res = c.get('/users', query_string={'q': 't3st'})
            html = res.get_data(as_text=True)

            # Test search for user
            self.assertIn('t3st', html)

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp
        
    def test_users_show(self):
        """Test that user page is shown 
        and that an invalid user id returns a 404 page"""

        with self.client as c:
            res = c.get(f'/users/{self.test_user.id}')
            html = res.get_data(as_text=True)

            # Should be a successful query
            self.assertIn(self.test_user.username, html)

            res = c.get(f'/users/01010')

            # Should return 404 page
            self.assertEqual(res.status_code, 404)

    def test_show_following(self):
        """Test that a user that is not logged in gets redirected
        and that a logged in user gets a page returned"""
        with self.client as c:
            res = c.get(f'/users/{self.test_user.id}/following')

            self.assertEqual(res.status_code, 302)
            
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id
            
            res = c.get(f'/users/{self.test_user.id}/following')
            
            self.assertEqual(res.status_code, 200)

    def test_users_followers(self):
        """Test that a user that is not logged in gets redirected
        and that a logged in user gets a page returned"""
        with self.client as c:
            res = c.get(f'/users/{self.test_user.id}/followers')

            self.assertEqual(res.status_code, 302)
            
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id
            
            res = c.get(f'/users/{self.test_user.id}/following')
            
            self.assertEqual(res.status_code, 200)
    
    def test_add_follow(self):
        """Test that a user that is not logged in gets redirected
        and that a logged in user adds a follow,
        or 404 if the followed user is not found"""
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id

            res = c.post(f'/users/follow/3232')

            # User not found
            self.assertEqual(res.status_code, 404)

            res = c.post(f'/users/follow/{self.user2_id}', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(self.test_user2.username, html)
            
            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]

            res = c.post(f'/users/follow/{self.user2_id}')
            
            # Not logged in, should redirect
            self.assertEqual(res.status_code, 302)
            
    def test_stop_following(self):
        """Test that a user that is not logged in gets redirected
        and that a logged in user can unfollow,
        or 404 if the unfollowed user is not found"""
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id

            c.post(f'/users/follow/{self.user2_id}') # User follow user2

            res = c.post(f'users/stop-following/{self.user2_id}', follow_redirects=True)
            html = res.get_data(as_text=True)

            # Should unfollow successfully
            self.assertEqual(res.status_code, 200)
            self.assertNotIn(self.test_user2.username, html)

            res = c.post(f'/users/stop-following/234')
            
            # Should return 404
            self.assertEqual(res.status_code, 404)

            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]

            res = c.post(f'/users/stop-following/{self.user2_id}')
            
            # Not logged in, should redirect
            self.assertEqual(res.status_code, 302)
    
    def test_profile(self):
        """Test updating profile: should update if correct password provided, 
        same page if password incorrect password or no password provided,
        and a get request returns a page with a 200 status code.
        """
        with self.client as c:
            
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id

            # Get should return page with 200 status code
            res = c.get('/users/profile')

            self.assertEqual(res.status_code, 200)

            # Should update profile successfully
            data = dict(password=self.user_pass)
            res = c.post('/users/profile', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('You updated your profile', html)

            # Should return the same page - No password provided
            data = dict(username='h1h1h1h1')
            res = c.post('/users/profile', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Edit Your Profile.', html)

            # Should return the same page - Wrong password
            data = dict(password='h1h1h1h1')
            res = c.post('/users/profile', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Incorrect credentials', html)
    
    def test_delete_user(self):
        """Test that if a user is logged in, their account is deleted.
        """
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id

            res = c.post(f'/users/delete', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Sign up', html)
    
    def test_add_like(self):
        """Test that a user adds a like, and that a user can dislike."""
        # Instance <Message at 0x18dd5429c08> is not bound to a Session 
        msg = Message(user_id=self.test_user.id, text='hjelo')

        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2_id

            res = c.post(f'/users/add_like/{msg.id}')
            # html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
    
    def test_show_likes(self):
        """Test that a user can see likes"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id

            res = c.get(f'/users/{self.test_user.id}/likes')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(self.test_user.username, html)