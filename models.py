from google.appengine.ext import ndb

# [START user]
class User(ndb.Model):
    """Sub model for representing a user."""
    #identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(required=True)
    team = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    #TODO: link Team to User
    team_img = ndb.StringProperty(required=False)

    @classmethod
    def by_name(cls, name):
        print '#### get by name =   %s' % name
        #u = User.all().filter('name =', name).get()
        u = User.gql("WHERE name = :name", name = name)
        result = u.get()
        return result

    @classmethod
    def by_email(cls, email):
        print '#### get by email =   %s' % email
        #u = User.all().filter('email =', email).get()
        u = User.gql("WHERE email = :email", email = email)
        result = u.get()
        return result

# [START audit]
class Audit(ndb.Model):
    """A main model for representing an individual Audit entry."""
    user = ndb.StructuredProperty(User)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class Team(ndb.Model):
    admin = ndb.StringProperty(required=True)
    team_name = ndb.StringProperty(required=True)
    organization_type = ndb.StringProperty(required=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    team_img = ndb.StringProperty(required=False)
    members = ndb.StringProperty(repeated=True)

    @classmethod
    def by_team_name(cls, team_name):
        t = Team.gql("WHERE team_name = :team_name", team_name)
        result = t.get()
        return result
