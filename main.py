import webapp2
import cgi
import time
import urllib
import logging

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import mail
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

VVS_CHAT_NAME = 'vvs_chat'

def chat_key(chat_name=VVS_CHAT_NAME):
    """Constructs a Datastore key for a Chat entity."""
    return ndb.Key('ChatMessage', chat_name)


class ChatRoom(object):
	"""A chatroom"""

	rooms = {}

	def __init__(self,name):
		self.name = name
		self.users =[]
		self.messages = []
		ChatRoom.rooms[name] = self

	def addSubscriber(self,subscriber):
		self.users.append(subscriber)
		subscriber.sendMessage(self.name,"Benutzer %s hat den Raum betreten." % subscriber.username)

	def removeSubscriber(self,subscriber):
		if subscriber in self.users:
			subscriber.sendMessage(self.name,"Benutzer %s hat den Raum verlassen." % subscriber.username)
			self.users.remove(subscriber)

	def addMessage(self,msg):
		self.messages.append(msg)

	def printMessages(self,out):
		print >> out, "Chat Nachrichten von: %s" % self.name
		for i in self.messages:
			print >> out,i

class ChatUser(ndb.Model):
	"""A user participating in chats"""
	username = ndb.StringProperty(indexed=False)

	def setUsername(self,username):
		self.username= username

	def subscribe(self,roomname):
		if roomname in ChatRoom.rooms:
			room = ChatRoom.rooms[roomname]
			self.rooms[roomname] = room
			room.addSubscriber(self)
		else:
			raise ChatError("Den Raum %s gibt es nicht" % roomname)

	def sendMessage(self,roomname,text):
		if roomname in self.rooms: 
			room = self.rooms[roomname]
			cm = ChatMessage(self,text)
			room.addMessage(cm)
		else:
			raise ChatError("Benutzer %s ist nicht im Chatraum %s" % self.username, roomname)

	def displayChat(self,roomname,out):
		if roomname in self.rooms:
			room = self.rooms[roomname]
			room.printMessages(out)
		else:
			raise ChatError("Benutzer %s ist nicht im Chatraum %s" % self.username, roomname)


class ChatMessage(ndb.Model):
	sender = ndb.StructuredProperty(ChatUser)
	timestamp = ndb.DateTimeProperty(auto_now_add=True)
	msg = ndb.TextProperty(indexed=False)

	def setUser(self,user):
		self.sender = user

	def setMessage(self,message):
		self.msg = message

	def __str__(self):

		return "%s von %s um %s : %s" % (self.timestamp.strftime("%d.%m.%Y"),self.sender.username,self.timestamp.strftime("%H:%M:%S"),self.msg)

Messages = []
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(
        	"""<html>
				<head>
				    <title>Welcome to ColinCC</title>
				    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
				    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap-theme.min.css">
				    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
				    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js"></script>
				</head>
				<body>
				<div class="panel panel-default">
				    <div class="panel-heading">
				        <h3>
				            <small>VVS - 2015 - Oliver Colin Sauer</small>
				        </h3>
				    </div>
				    <div class="panel-body">
				        <div class="panel panel-default">
				        
				        <div class="panel-heading">
				        	<h4>%s</h4>
				        </div>
				            """ % VVS_CHAT_NAME)
        #global Messages
        #if len(Messages) > 10:
        #	chat = Messages[-10:]
        #else:
        #	chat = Messages
        chat_query = ChatMessage.query(
            ancestor=chat_key(VVS_CHAT_NAME)).order(-ChatMessage.timestamp)
        chat = chat_query.fetch(10)
        for msg in chat:
        	self.response.write("<p>%s</p>" % msg)
        self.response.write("""
				        </div>
				        <form action="/post" method="post">
				            <label>Name:</label><input type="text" class="form-control" name="username"/>
				            <label>Nachricht:</label>
				            <div><textarea name="message" rows="5" cols="60" class="form-control"></textarea></div>
				            <input type="submit" value="senden" class="btn btn-primary"/>
				        </form>
				    </div>
				    <div class="panel-footer">Server date and time: %s </div>
				</div>
				</body>
				</html>""" % time.strftime("%d.%m.%Y(%H:%M:%S)"))
	
class PostHandler(webapp2.RequestHandler):
	def post(self):
		if len(self.request.get("message")) > 1:
			chatter = ChatUser(parent=chat_key(VVS_CHAT_NAME))
			username = 'anonymous'
			if len(self.request.get("username")) > 1:
				username = self.request.get("username")
			chatter.setUsername(username)
			msg = ChatMessage(parent=chat_key(VVS_CHAT_NAME))
			msg.setUser(chatter)
			msg.setMessage(self.request.get("message"))
			msg.put()

		#global Messages
		#Messages.append(ChatMessage(chatter,msg))
		self.redirect('/')

class EmailHandler(webapp2.RequestHandler):
	def get(self):
		sender_address = "Oliver Colin Sauer <ocolins@gmail.com>"
		my_address = "ocolins@gmail.com"
		subject = "VVS-Chat-Message"
		content = "Dies ist eine Email aus dem VVS-Chat"
		mail.send_mail(sender_address,my_address,subject,content)
		self.response.write('Email wurde gesendet')

		
class IncomingMailHandler(InboundMailHandler):
	def receive(self,mail_message):
		chatter = ChatUser(parent=chat_key(VVS_CHAT_NAME))
		chatter.setUsername(mail_message.sender)
		msg = ChatMessage(parent=chat_key(VVS_CHAT_NAME))
		msg.setUser(chatter)
		text_bodies = mail_message.bodies('text/plain')
		html_bodies = mail_message.bodies('text/html')
		email_body = ''
		for content_type,body in html_bodies:
			email_body += body.decode()
		for content_type,body in text_bodies:
			email_body += body.decode()

		sender_address = "Oliver Colin Sauer <ocolins@gmail.com>"
		my_address = "ocolins@gmail.com"
		subject = "VVS-Chat-Message von " + mail_message.sender
		mail.send_mail(sender_address,my_address,subject,email_body)

		msg.setMessage(email_body)
		msg.put()
		logging.info('Received email from'+mail_message.sender)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/post', PostHandler),
    ('/email', EmailHandler),
    IncomingMailHandler.mapping()
], debug=True)