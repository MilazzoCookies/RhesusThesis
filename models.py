from app import db

# mongoengine database module
from mongoengine import *
from datetime import datetime
import logging

class Comment(EmbeddedDocument):
	name = StringField()
	comment = StringField()
	timestamp = DateTimeField(default=datetime.now())
	
class User(db.Document):
	# fake it on the front end and just lable the email as username
	email = db.StringField(unique=True)
	# username = db.StringField(default=True)
	password = db.StringField(default=True)
	active = db.BooleanField(default=True)
	isAdmin = db.BooleanField(default=False)
	timestamp = db.DateTimeField(default=datetime.now())

class Idea(Document):
	# creator = db.ReferenceField(User)
	creator = StringField(max_length=120, required=True, verbose_name="First name")
	idea = StringField(max_length=120, required=True)
	tagline = StringField(max_length=120, required=True)
	slug = StringField()
	idea = StringField(required=True, verbose_name="What is your idea?")

	# Category is a list of Strings
	categories = ListField(StringField(max_length=30))

	# rhesusThesis is a list of strings
	rhesusThesis = ListField(StringField(max_length=30))

	#expanding list of users
	allUsers = ListField(StringField(max_length=30))

	# Comments is a list of Document type 'Comments' defined above
	comments = ListField( EmbeddedDocumentField(Comment) )

	# Timestamp will record the date and time idea was created.
	timestamp = DateTimeField(default=datetime.now())




class Note(db.Document):
	title = db.StringField(required=True,max_length=120)
	content = db.StringField()
	last_updated = db.DateTimeField(default=datetime.now())
	user = db.ReferenceField(User)