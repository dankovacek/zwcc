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

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]
# os.path.dirname(__file__)
#jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
#    autoescape = True)

DEFAULT_GUESTBOOK_NAME = 'Zero Waste City Challenge'

# We set a parent key on the 'Audits' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

# add handler for easier write calls

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = JINJA_ENVIRONMENT.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)


# [START user]
class User(ndb.Model):
    """Sub model for representing a user."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('username =', name).get()
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
    team_type = ndb.StringProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END audit]


# [START main_page]
class MainPage(Handler):

    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        audits_query = Audit.query(
            ancestor=guestbook_key(guestbook_name)).order(-Audit.date)
        audits = audits_query.fetch(10)

        user = users.get_current_user()

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        print '$$$$$$$$$$$4 url_linktext = %s' % url_linktext

        self.render('index.html')
        self.render('header.html', url=url, url_linktext=url_linktext,
            guestbook_name=guestbook_name, user=user)
        self.render('content.html', user=user, audits=audits,
            guestbook_name=urllib.quote_plus(guestbook_name), url=url)
# [END main_page]


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
        pass

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
], debug=True)
# [END app]
