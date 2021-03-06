import os, datetime
from flask import current_app, Blueprint, render_template, abort, request, flash, redirect, url_for, jsonify
from flask.ext.login import (current_user, login_required, login_user, logout_user, confirm_login, fresh_login_required)
from flask import jsonify
import re
from jinja2 import TemplateNotFound

from unidecode import unidecode
import models
from libs.User import User
import random, string


from flask.ext.mongoengine import MongoEngine

thesisIdeas_app = Blueprint('thesisIdeas_app', __name__, template_folder='templates')

# import data models
import models

# hardcoded categories for the checkboxes on the form
categories = ['web', 'software', 'physical computing','video','audio','installation',]
rhesusThesis = ['RHESUS','THESIS'] #for a dropdown
# forUser = models.allUsers
# allUsers = ['Tony Baloney']

@thesisIdeas_app.route("/", methods=['GET','POST'])
def index():

	# if form was submitted and it is valid...
	if request.method == "POST":
	
		# get form data - create new idea
		idea = models.Idea()
		idea.creator = request.form.get('creator','anonymous')
		idea.tagline = request.form.get('tagline','no tagline')
		idea.slug = slugify(idea.tagline + " " + idea.creator)
		idea.idea = request.form.get('idea','')
		idea.categories = request.form.getlist('categories') # getlist will pull multiple items 'categories' into a list
		idea.rhesusThesis = request.form.getlist('rhesusThesis')
		idea.forUser = request.form.getlist('forUser')
		# models.allUsers = request.form.getlist('allUsers')


		idea.save() # save it

		# redirect to the new idea page
		return redirect('/ideas/%s' % idea.slug)

	else:
		# for form management, checkboxes are weird (in wtforms)
		# prepare checklist items for form
		# you'll need to take the form checkboxes submitted
		# and idea_form.categories list needs to be populated.
		if request.method=="POST" and request.form.getlist('categories', 'rhesusThesis'):
			for c in request.form.getlist('categories'):
				idea_form.categories.append_entry(c)

			for r in request.form.getlist('rhesusThesis'):
				idea_form.rhesusThesis.append_entry(r)


		# render the template
		templateData = {
			'ideas' : models.Idea.objects().order_by('-timestamp'),
			'categories' : categories,
			# 'creators' : creator,
			# 'tagline' : models.Idea.objects(),
			'allUsers' : models.User.objects(),
			'rhesusThesis' : rhesusThesis
		}
		# app.logger.debug(templateData)

		return render_template("main.html", **templateData)




@thesisIdeas_app.route("/forUser/<for_user>")
def by_userFor(for_user):

	# try and get ideas where cat_name is inside the categories list
	try:
		ideas = models.Idea.objects(forUser= for_user)

	# not found, abort w/ 404 page
	except:
		abort(404)

	# prepare data for template
	templateData = {
		'current_forUser' : {
			'slug' : for_user,
			'name' : for_user.replace('_',' '),
		},
		'ideas' : ideas,
		# 'tagline' : tagline,
		'categories' : categories,
		'rhesusThesis': rhesusThesis
	}

	# render and return template
	return render_template('for_user.html', **templateData)


##### trying to get all_users from models and match it 
##### up with the ideas that have the same creator

@thesisIdeas_app.route("/allUsers/<all_users>")
def by_users(all_users):

	# try and get ideas where all_users is inside the creator list
	try:
		ideas = models.Idea.objects(creator=all_users)

	# not found, abort w/ 404 page
	except:
		abort(404)

	# prepare data for template
	templateData = {
		'current_allUsers' : {
			'slug' : all_users,
			'name' : all_users.replace('_',' '),
		},
		'ideas' : ideas,
		# 'tagline' : tagline,
		# 'creators' : creator,
		# 'rhesusThesis': rhesusThesis
	}
	return render_template('all_users.html', **templateData)


@thesisIdeas_app.route("/category/<cat_name>")
def by_category(cat_name):

	# try and get ideas where cat_name is inside the categories list
	try:
		ideas = models.Idea.objects(categories=cat_name)

	# not found, abort w/ 404 page
	except:
		abort(404)

	# prepare data for template
	templateData = {
		'current_category' : {
			'slug' : cat_name,
			'name' : cat_name.replace('_',' '),
		},
		'ideas' : ideas,
		# 'tagline' : tagline,
		'categories' : categories,
		'rhesusThesis': rhesusThesis
	}

	# render and return template
	return render_template('category_listing.html', **templateData)

@thesisIdeas_app.route("/rhesusThesis/<rhesus_or_thesis>")
def by_rhesus_or_thesis(rhesus_or_thesis):

	# try and get ideas where cat_name is inside the categories list
	try:
		ideas = models.Idea.objects(rhesusThesis=rhesus_or_thesis)

	# not found, abort w/ 404 page
	except:
		abort(404)

	# prepare data for template
	templateData = {
		'current_rhesusThesis' : {
			'slug' : rhesus_or_thesis,
			'name' : rhesus_or_thesis.replace('_',' ')
		},
		'ideas' : ideas,
		# 'tagline' : tagline,
		# 'creators' : creator,
		'rhesus_or_thesis' : rhesusThesis
	}

	# render and return template
	return render_template('rhesus_or_thesis.html', **templateData)

@thesisIdeas_app.route("/tagline/<tag_line>")
def by_tag_line(tag_line):

	# try and get ideas where cat_name is inside the categories list
	try:
		ideas = models.Idea.objects(tagline=tag_line)

	# not found, abort w/ 404 page
	except:
		abort(404)

	# prepare data for template
	templateData = {
		'current_category' : {
			'slug' : tagline,
			'name' : tag_line.replace('_',' ')
		},
		'ideas' : ideas,
		'tagline' : tagline,
		'rhesus_or_thesis' : rhesusThesis
	}

	# render and return template
	return render_template('rhesusThesis_listing.html', **templateData)


@thesisIdeas_app.route("/ideas/<idea_slug>")
def idea_display(idea_slug):

	# get idea by idea_slug
	try:
		ideasList = models.Idea.objects(slug=idea_slug)
	except:
		abort(404)

	# prepare template data
	templateData = {
		'idea' : ideasList[0]
	}

	# render and return the template
	return render_template('idea_entry.html', **templateData)

@thesisIdeas_app.route("/ideas/<idea_id>/comment", methods=['POST'])
def idea_comment(idea_id):

	name = request.form.get('name')
	comment = request.form.get('comment')

	if name == '' or comment == '':
		# no name or comment, return to page
		return redirect(request.referrer)


	#get the idea by id
	try:
		idea = models.Idea.objects.get(id=idea_id)
	except:
		# error, return to where you came from
		return redirect(request.referrer)


	# create comment
	comment = models.Comment()
	comment.name = request.form.get('name')
	comment.comment = request.form.get('comment')
	
	# append comment to idea
	idea.comments.append(comment)

	# save it
	
# old data was giving problems
	if idea.tagline == None: 
		idea.tagline = ' '
	idea.save()

	return redirect('/ideas/%s' % idea.slug)

@thesisIdeas_app.route("/about")
def about_rhesusthesis():
	
	return render_template('about.html')


@thesisIdeas_app.errorhandler(404)
def page_not_found(error):
	return render_template('404.html'), 404


# slugify the tagline 
# via http://flask.pocoo.org/snippets/5/
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim=u'-'):
	"""Generates an ASCII-only slug."""
	result = []
	for word in _punct_re.split(text.lower()):
		result.extend(unidecode(word).split())
	return unicode(delim.join(result))

# the jsonify code is here
@thesisIdeas_app.route('/data/ideas')
def data_ideas():

	# query for the ideas - return oldest first, limit 10
	ideas = models.Idea.objects().order_by('+timestamp').limit(10)

	if ideas:

		# list to hold ideas
		public_ideas = []

		#prep data for json
		for i in ideas:
			
			tmpIdea = {
				'creator' : i.creator,
				'tagline' : i.tagline,
				'idea' : i.idea,
				'timestamp' : str( i.timestamp )
			}

			# comments / our embedded documents
			tmpIdea['comments'] = [] # list - will hold all comment dictionaries
			
			# loop through idea comments
			for c in i.comments:
				comment_dict = {
					'name' : c.name,
					'comment' : c.comment,
					'timestamp' : str( c.timestamp )
				}

				# append comment_dict to ['comments']
				tmpIdea['comments'].append(comment_dict)

			# insert idea dictionary into public_ideas list
			public_ideas.append( tmpIdea )

		# prepare dictionary for JSON return
		data = {
			'status' : 'OK',
			'ideas' : public_ideas
		}

		# jsonify (imported from Flask above)
		# will convert 'data' dictionary and set mime type to 'application/json'
		return jsonify(data)

	else:
		error = {
			'status' : 'error',
			'msg' : 'unable to retrieve ideas'
		}
		return jsonify(error)


#pulling data from existing JSON on another site
@thesisIdeas_app.route("/data/grab")
def data_grab():

	# fetch Ideas JSON
	ideas = requests.get('http://omgclothes.herokuapp.com/data/ideas')
	
	# get ideas from JSON
	itpIdeas = ideas.json().get('ideas')
	
	# log out the content of the request
	app.logger.debug(itpIdeas)
	
	# prepare template data
	templateData = {
		'ideas' : itpIdeas
	}
	
	return render_template("main.html", **templateData)
