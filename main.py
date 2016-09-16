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
import os
import jinja2
import webapp2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Posts(db.Model):
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class NewPosts(Handler):
    def render_base(self, title="", blog="", error=""):
        self.render("front_page.html", title=title, blog = blog, error=error)

    def get(self):
        self.render_base()

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            b = Posts(title = title, blog = blog)
            b.put()
            self.redirect("/")

        else:
            error = "We need both a title and a blog post!"
            self.render_base(title, blog, error)


class BlogPosts(Handler):
    def render_blog(self, title="", blog="", error=""):
        blog_posts = db.GqlQuery("SELECT * from Posts ORDER BY created DESC LIMIT 5")
        self.render("posts.html", title=title, blog=blog, error=error, blog_posts=blog_posts)

    def get(self):
        self.render_blog()


class ViewPostHandler(Handler):
    def get(self, id):
        post = (Posts.get_by_id(int(id)))
        if post:
            self.render("permalink.html", post=post)
        else:
            error="This post does not exist"
            self.render("permalink.html", post=post, error=error)

app = webapp2.WSGIApplication([
    webapp2.Route('/', BlogPosts),
    webapp2.Route('/new-posts', NewPosts),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
