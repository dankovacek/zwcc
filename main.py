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
import re
import json

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import memcache

import jinja2
import webapp2

# code for sessions module
# http://webapp2.readthedocs.io/en/latest/_modules/webapp2_extras/sessions.html
from webapp2_extras import sessions

import xlrd
import datetime
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from models import User
from models import Team

import data

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# webapp2 session configuration
# http://stackoverflow.com/questions/13421614/missing-configuration-keys-
# for-webapp2-extras-sessions-secret-key
config = {}

config['webapp2_extras.sessions'] = {
    'secret_key': 'some-secret-key',
}

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
    #http://webapp2.readthedocs.io/en/latest/_modules/webapp2_extras/appengine/sessions_memcache.html
    #http://stackoverflow.com/questions/33921819/using-sessions-with-webapp2-python
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

# [START main_page]
class MainPage(Handler):
    def get(self):
        user_email = self.session.get('email')

        # guestbook_name = self.request.get('guestbook_name',
        #                                   DEFAULT_GUESTBOOK_NAME)
        # audits_query = Audit.query(
        #     ancestor=guestbook_key(guestbook_name)).order(-Audit.date)
        # audits = audits_query.fetch(10)

        # user = users.get_current_user()

        #TODO: query audit entities
        audits = ''
        if user_email:
            #retrieve the User object from database
            u = User.by_email(user_email)
            print '#######user email = %s' % u

        else:
            #url = users.create_login_url(self.request.uri)
            u = None

        upload_url = blobstore.create_upload_url('/upload')


        self.render('index.html', user=u, upload_url=upload_url)


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


# [START spreadsheet_import]

class Login(Handler):
    def get(self):
        self.render('login.html', user='', login_out='login')

    def post(self):
        email = self.request.get('email')
        pwd = self.request.get('password')
        email_error, password_error = None, None

        # if login isn't in DB, redirect to signup page
        user = User.by_email(email)
        if user is None:
            self.redirect('/signup')
            return

        if not email:
            email_error = "Please use a valid e-mail address."

        #validate password
        #http://stackoverflow.com/questions/2990654/how-to-test-a-regex-password-in-python
        if not re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', pwd):
            pwd_error1 = "Password must be alphanumeric and > 8 characters."

        print '############   user passord = %s ' % user
        if user.password != pwd:
            pwd_error2 = "Incorrect password."

        if (email_error or password_error):
            self.render("login.html", email=email,
                email_error=email_error, pwd_error1=pwd_error1,
                pwd_error2=pwd_error2)
            self.render('header.html', user='')
        else:
            self.session['email'] = email
            self.render("index.html", user=user)

class Signup(Handler):
    def get(self):
        t = ['Vancouver', 'San Francisco', 'Toronto', 'New York City']
        self.render('signup.html', user='', teams=t)

    def post(self):
        username = self.request.get('username')
        email = self.request.get('email')
        password = self.request.get('password')
        new_org_name = self.request.get("org_name")

        org_type = self.request.get("org_type")

        selected_existing_team = self.request.get("teams")

        #team_img = self.request.get("team_image")
        email_error, team_error, uname_error, pwd_error = '','','',''

        # user = User.by_email(email)
        # if user:
        #     user_error = "User account already exists"

        if not email:
            email_error = "Please use a valid email."

        if not (new_org_name and selected_existing_team):
            team_error = "Please put a valid team name."

        if not username:
            uname_error = "Please enter a username."

        #use placeholder existing teams
        #could be also done by keys-only query to teams
        #filter by team_name
        t = ['Vancouver', 'San Francisco', 'Toronto', 'New York City']

        #validate password
        #http://stackoverflow.com/questions/2990654/how-to-test-a-regex-password-in-python
        if not re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
            pwd_error = "Please enter an alphanumeric password >= 8 characters long."

        if (email_error or team_error or uname_error or pwd_error):
            self.render("signup.html", username=username, email=email,
                team=new_org_name, uname_error=uname_error,
                team_error=team_error, email_error=email_error,
                pwd_error=pwd_error, teams=t, org_type=org_type)
            print 'what friggin error? %s, %s, %s, %s' % (email_error,
                team_error, uname_error, pwd_error)
        else:
            #check if team exists
            #join user to existing team
            print 'selected_existing_team?? = %s' % selected_existing_team
            print 'org_type?? = %s' % org_type
            if new_org_name:
                create_new_team(username, new_org_name, org_type)
                create_user(username, email, password, selected_existing_team, self.session)
            else:
                tm = Team.by_team_name(selected_existing_team)
                members = tm.members
                #store member names as a comma delimited string
                members += [username]
                #update team members
                team.members.put()
                create_user(username, email, password, members, selected_existing_team, self.session)

            user = User.by_name(username)
            self.render('index.html', user=user, teams=t)



def create_user(name, email, password, team_name, session_obj):
    u = User.by_email(email)

    # check if user already exists.
    if not u:
        new_user = User(name=name, password=password, email=email, team=team_name)
        new_user.put()


def create_new_team(admin, team_name, organization_type):
    new_team = Team(admin=admin, team_name=team_name, members=[admin],
        organization_type=organization_type)
    new_team.put()

class Logout(Handler):
    def get(self):
        self.session['email'] = None
        self.redirect('/')
        return

class Challenges(Handler):
    def get(self):
        self.render('challenges.html', user='')
        return

class Data(Handler):
    def get(self):
        self.render('data.html', user='')
        return

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/signup', Signup),
    ('/login', Login),
    ('/logout', Logout),
    ('/upload', data.UploadHandler),
    ('/challenges', Challenges),
    ('/data', Data)
], debug=True, config=config)
# [END app]
