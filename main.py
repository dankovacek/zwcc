#!/usr/bin/env python

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
from webapp2_extras import sessions

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# webapp2 session configuration
config = {}

config['webapp2_extras.sessions'] = {
    'secret_key': 'some-secret-key',
}

# [END imports]
# os.path.dirname(__file__)
#jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
#    autoescape = True)

#DEFAULT_GUESTBOOK_NAME = 'Team Name'

# We set a parent key on the 'Audits' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

# add handlers for easier write calls
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = JINJA_ENVIRONMENT.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    #get a session store for this request
    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)

        try:
            #Dispatch the request
            webapp2.RequestHandler.dispatch(self)
        finally:
            #save all sessions
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()


def guestbook_key(guestbook_name='temp'):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)


# [START user]
class User(ndb.Model):
    """Sub model for representing a user."""
    #identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(required=True)
    team = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)

    date = ndb.DateTimeProperty(auto_now_add=True)
    #TODO: link Team to User
    team_img = ndb.StringProperty(required=True)

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def by_email(cls, email):
        u = User.all().filter('email =', email).get()
        return u

# [START audit]
class Audit(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    user = ndb.StructuredProperty(User)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class Team(ndb.Model):
    admin = ndb.StructuredProperty(User)
    team_name = ndb.StringProperty(required=True)
    organization_type = ndb.StringProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    team_img = ndb.StringProperty(required = False)

    @classmethod
    def by_team_name(cls, name):
        t = Team.all().filter('team_name =', name).get()
        return t

    @classmethod
    def by_user_email(cls, email):
        u = User.all().filter('email =', email).get()
        team_name = u.team
        t = by_team_name(team_name)
        return t

# [END audit]


# [START main_page]
class MainPage(Handler):
    def get(self):
        user_email = self.session.get('email')

        print '#######user email = %s' % user_email

        # guestbook_name = self.request.get('guestbook_name',
        #                                   DEFAULT_GUESTBOOK_NAME)
        # audits_query = Audit.query(
        #     ancestor=guestbook_key(guestbook_name)).order(-Audit.date)
        # audits = audits_query.fetch(10)

        # user = users.get_current_user()

        #TODO: query audit entities
        audits = ''
        if user_email:
            #url = users.create_logout_url(self.request.uri)
            url = '/logout'
            url_linktext = 'Logout'

            #retrieve the User object from database
            u = User.by_email(user_email)
        else:
            #url = users.create_login_url(self.request.uri)
            url = '/login'
            url_linktext = 'Login'
            u = None

        self.render('index.html')
        self.render('header.html', user=u, url_linktext=url_linktext, url=url)
        self.render('content.html', user=u, audits=audits, url=url)
# [END main_page]

# TODO: implement create Team Entity
# def CreateTeam(self, email, team_name):
#     t = Team.by_email(email)
#     # check if user already exists.

#     if u:
#         msg = 'User already registered.'
#         self.redirect('/')
#     else:
#         new_user = User(username=session_obj['username'],
#             email=session_obj['email'], picture=session_obj['picture'],
#             provider=session_obj['provider'],
#             provider_id=session_obj['provider_id'])
#         new_user.put()
#         user = getUserInfo(self, session_obj['email'])
#         #return user


# [START guestbook]
class Guestbook(webapp2.RequestHandler):
    def post(self):
        # We set the same parent key on the 'Audit' to ensure each
        # Audit is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        audit = Audit(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            audit.user = User(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        audit.content = self.request.get('content')
        audit.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))
# [END guestbook]

class Login(Handler):
    def get(self):
        self.render('login.html', user='', login_out='login')
        self.render('header.html', team_name='')

    def post(self):
        email = self.request.get('email')
        pwd = self.request.get('password')
        email_error, password_error = None, None

        # user = User.by_email(email)
        # if user:
        #     user_error = "User account already exists"

        #u = User.by_email(email)

        if not email:
            email_error = "Please use a valid e-mail address."

        if not pwd:
            password_error = "Please use only alphanumeric characters."

        if (email_error or password_error):
            self.render("login.html", email=email,
                email_error=email_error, password_error=password_error)
            self.render('header.html', user='', url='', login_out='login')
        else:
            self.redirect("/")

class Signup(Handler):
    def get(self):
        self.render('signup.html', user='', login_out='login')
        self.render('header.html', team_name='')

    def post(self):
        username = self.request.get('username')
        email = self.request.get('email')
        team = self.request.get("team")
        #team_img = self.request.get("team_image")
        email_error, team_error, uname_error = None, None, None


        # user = User.by_email(email)
        # if user:
        #     user_error = "User account already exists"

        if not email:
            email_error = "Please use a valid email."

        if not team:
            team_error = "Please put a valid team name."

        if not username:
            uname_error = "Please enter a username."

        if (email_error or team_error):
            self.render("login.html", username=username, email=email, team=team,
             uname_error=uname_error, team_error=team_error, email_error=email_error)
            self.render('header.html', team_img='', login_out='login')
        else:
            #create a new user
            create_user(username, email, team)
            self.redirect("/")

def create_user(name, email, team_name):
    u = User.by_email(email)

    print 'email here?  %s' % u.email

    # check if user already exists.
    if u:
        #msg = 'User already registered.'
        self.redirect('/')
    else:
        new_user = User(name=name, email=email, team=team_name)
        new_user.put()
        self.session['email'] = u.email
        self.redirect('/')

class Logout(Handler):
    def get(self):
        logout_url = 'http://localhost:8080' + users.create_logout_url('/')
        #user = users.get_current_user()
        print '##########  user %s' % user
        self.render('login.html', user=user, login_out='login',
            logout_url=logout_url)
        self.render('header.html', user=user, team_name='')

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
    ('/signup', Signup),
    ('/login', Login),
    ('/logout', Logout),
], debug=True, config=config)
# [END app]
