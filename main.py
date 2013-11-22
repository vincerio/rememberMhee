#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
#
#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import datetime
import cgi
import os
import re
import random
import hashlib
import hmac
import logging
import json
from string import letters

import webapp2
import jinja2
from google.appengine.ext import blobstore
from google.appengine.api import images
from google.appengine.api import users
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape = False)

			
##html input escape
def escape_html(s):
	return cgi.escape(s, quote = True)
		

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
		
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
		
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
		
    def render_json(self, d):
        json_txt = json.dumps(d)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json_txt)



class Tasks(db.Model):
	description = db.StringProperty()
	completed = db.BooleanProperty(default=False)
				

class MainHandler(Handler):
    def get(self):
		self.render('base.html')
	
class TasksHandler(Handler):
	def post(self):
		desc = self.request.get('description')
		t = Tasks(description = desc)
		t.put()
		tid = str(t.key().id())
		self.redirect('/tasks/%s' %tid)
	


	def get(self):
		tasks = Tasks.all()
		data = { 'tasks' : tasks }
		self.render('tasks.html',**data)

class SingleTaskHandler(Handler):		
	def put(self):
		desc = self.request.get('description')
		com = self.request.get('completed')
		url = self.request.url
		position = url.find('tasks')
		id = url[position+6:]
		task = Tasks.get_by_id(int(id))
		task.description = desc
		task.completed = bool(com)
		task.put()	

	def delete(self):
		url = self.request.url
		position = url.find('tasks')
		id = url[position+6:]
		task = Tasks.get_by_id(int(id))
		task.delete()
		
	def get(self):
		url = self.request.url
		position = url.find('tasks')
		id = url[position+6:]
		task = Tasks.get_by_id(int(id))
		data = { 'url': url , 'id':id , 'task':task}
		
		self.render('showtask.html',**data)
		
			
					
app = webapp2.WSGIApplication([
    ('/', MainHandler),
	('/tasks', TasksHandler),
	('/tasks/.*', SingleTaskHandler)

	
], debug=True)
