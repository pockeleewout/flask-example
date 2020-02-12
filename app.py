# Copyright 2020 Ewout Pockelé
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# General imports
from typing import *

###############################################################################
#  Part 1: Creating an application object

# This part is the basis of any flask application

# Import the things we need from Flask
import flask
from flask import Flask

# Create the Flask application object, giving it a name
#  I also tell it to serve all files from the 'static' folder on
#  the webserver root.  This is for simplicity in the example, but should not
#  be required for a more standard web-app
app = Flask(__name__.split(".")[0], static_url_path="")


# This is a 'route', or URL that the webserver should serve to users
@app.route('/')
# This function name can be anything, but please name it clearly
def index():
    # We redirect to the index.html file, which is from the 'static' folder
    #  Normally we would have to redirect to '/static/index.html', but because
    #  we told the webserver to serve all the static files and
    #  folders in '/', that is not required here.
    return flask.redirect("/index.html")


###############################################################################
#  Part 2: Database object and models

# For this part we will user Flask-SQLAlchemy, but most of the
#  documentation can be found in the SQLAlchemy project.
#   https://flask-sqlalchemy.palletsprojects.com/en/2.x/
#   https://docs.sqlalchemy.org/en/13/index.html

# Import the things we need from Flask-SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Set default configuration options for Flask-SQLAlchemy
app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///database.sqlite3")
app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

# Create the Flask-SQLAlchemy database management object
db = SQLAlchemy(app)


########################################
#  Part 2.a: Creating the model(s)

# Create a user object that will be stored in the database
#  This is done by subclassing 'db.Model', which provides everything
#  we need to do this.
class User(db.Model):
    """This class models users on our site"""

    # Create a property that is a column in the user table in the database
    #  We also specify it as a primary key, and that it should automatically
    #  increment as new objects are created.
    #
    #  See
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # We specify that a user's name should be unicode text, and should be unique
    name = db.Column(db.UnicodeText, unique=True, default=None)

    # Here we define a 'private' attribute, and we manually specify the column
    #  name to be 'gender'.  We also tell SQLAlchemy that the column can be
    #  NULL, and we also set NULL as the default value
    _gender = db.Column("gender", db.UnicodeText, nullable=True, default=None)

    # It is good practice to put attributes behind a write function.
    #  This way, values can be checked before setting, giving more useful
    #  debug information when setting it to an invalid value.
    def set_name(self, name: str):
        """Set the name of a user"""
        if isinstance(name, str):
            self.name = name

    # This is an alternative way of using custom getters/setter with
    # transparancy to end-users
    @property
    def gender(self) -> Optional[str]:
        """Get the gender of a user"""
        return self._gender

    @gender.setter
    def gender(self, gender: str):
        """Set the gender of a user"""
        if isinstance(gender, str) and gender in ["male", "female"]:
            self._gender = gender

    # This is a utility function that will be used later
    #  This allows our User object to be converted to a Python dictionary.
    #  This is done with dict(user)
    def __iter__(self) -> Dict:
        yield "id", self.id
        yield "name", self.name
        yield "gender", self.gender


###############################################################################
#  Part 3: REST API and using the database models

# Import the things we need from Flask-RESTFul
import flask_restful.reqparse
import flask_restful.inputs
from flask_restful import Api, Resource

# Create the REST API object, defining all REST end-points should be prefixed
#  with the '/api/v1' part
api = Api(app, prefix="/api/v1")


# Define an argument parser for users
user_parser = flask_restful.reqparse.RequestParser()
user_parser.add_argument("name", type=str, help="Name of the user")
user_parser.add_argument("gender", type=str, choices=["male", "female"],
                         help="Gender of the user")


# Create a REST resource
class UserResource(Resource):
    # Define a HTTP GET method for this resource
    def get(self, user_id):
        # This line generates a query to get the user with the
        #  primary key user_id.  This works because we defined the primary
        #  key of our user to be his/her ID.
        user = User.query.get(int(user_id))

        # If the user does not exist, return nothing and a HTTP 400 Bad Request,
        #  or a HTTP 404 Not Found
        if not user:
            # Return an empty dictionary and a status code of 404
            return {}, 404

        # This returns to the client a JSON reply with the dictionary of user
        #  data.  This works because the User class has a method '__dict__',
        #  otherwise we would have to create the dictionary here.
        return dict(user)

    # Define an HTTP UPDATE method for this resource
    def update(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {}, 404

        # Parse the arguments passed
        args = user_parser.parse_args(strict=True)

        # If a name is in the arguments, update the user's name
        if "name" in args:
            user.set_name(args["name"])

        # If a gender is in the arguments, update the user's gender
        if "gender" in args:
            user.gender = args["gender"]

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! IMPORTANT
        # Write the user back to the database
        db.session.add(user)
        db.session.commit()

        # Return HTTP 204 No Content to indicate successful processing
        return None, 204


class AllUserResource(Resource):
    # Get all the users in the database
    def get(self):
        result: List[Dict] = []

        # Go over all users in the database using 'query.all()'
        for user in User.query.all():
            # Add that user's dictionary to the output
            result.append(dict(user))

        # Return all the users
        return result


    # Provide a way to create new users
    def post(self):
        # Parse the arguments given
        args = user_parser.parse_args(strict=True)

        # Create a new User object
        user = User()

        # Set the properties of the user
        user.set_name(args["name"])
        user.gender = args["gender"]

        # Write the new user to the database, note that we did not set the 'id'
        #  field.  SQLAlchemy will set this for us.
        db.session.add(user)
        db.session.commit()

        # Return HTTP 204 No Content to confirm addition
        return None, 204


# Add the resource to the REST API, using an int argument 'user_id'
api.add_resource(UserResource, "/user/<int:user_id>")
api.add_resource(AllUserResource, "/user")


###############################################################################
#  Part 4: Extra Flask stuff

@app.cli.command("create-db")
def create_db():
    db.create_all()

@app.cli.command("drop-db")
def drop_db():
    db.drop_all()
