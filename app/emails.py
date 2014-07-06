from flask import render_template, flash
from flask.ext.mail import Message
from app import mail
from decorators import async
from config import ADMINS

@async    
def send_async_email(msg):
    mail.send(msg)
    
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(msg)
    #thr = threading.Thread(target = send_async_email, args = [msg])
    #thr.start()

    
def follower_notification(followed, follower):
    send_email("[microblog] %s is now following you!" % follower.nickname,
        ADMINS[0],
        [followed.email],
        render_template("follower_email.txt", 
            user = followed, follower = follower),
        render_template("follower_email.html", 
            user = followed, follower = follower))

def outfit_email(Post, user):
    send_email("Here is the outfit you requested!",
        ADMINS[0],
        [user.email],
        render_template("post_email.txt", user = user),
        render_template("post_email.html", user = user))
    flash('We have emailed you the outfit')
    print Post, user.email, ADMINS[0]
        