from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField
from wtforms.validators import Required, Length, url
from flask.ext.babel import gettext
from wtforms.fields.html5 import URLField
from app.models import User

class LoginForm(Form):
    openid = TextField('openid', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)
    
class EditForm(Form):
    nickname = TextField('nickname', validators = [Required()])
    website = TextField('website', validators = [Required()])
    about_me = TextAreaField('about_me', validators = [Length(min = 0, max = 140)])
    
    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname
        
    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        if self.nickname.data != User.make_valid_nickname(self.nickname.data):
            self.nickname.errors.append(gettext('This nickname has invalid characters. Please use letters, numbers, dots and underscores only.'))
            return False
        user = User.query.filter_by(nickname = self.nickname.data).first()
        if user != None:
            self.nickname.errors.append(gettext('This nickname is already in use. Please choose another one.'))
            return False
        return True
        
class PostForm(Form):
    post = TextField('post', validators = [Required()])
    image = TextField('image', validators = [Required()])
    link1 = URLField('link1')
    link1_text = TextField('link1_text')
    link2 = URLField('link2')
    link2_text = TextField('link2_text')
    link3 = URLField('link3')
    link3_text = TextField('link3_text')
    link4 = URLField('link4')
    link4_text = TextField('link4_text')
    link5 = URLField('link5')
    link5_text = TextField('link5_text')

class SearchForm(Form):
    search = TextField('search', validators = [Required()])

class AddLink(Form):
    url = TextField('url', validators = [Required()])
    body = TextField('body', validators = [Required()])

class Scraper(Form):
    url = TextField('url', validators = [Required()])


class EditPostForm(Form):
    post = TextField('post', validators = [Required()])
    image = TextField('image', validators = [Required()])
    link1 = URLField('link1')
    link1_text = TextField('link1_text')
    link2 = URLField('link2')
    link2_text = TextField('link2_text')
    link3 = URLField('link3')
    link3_text = TextField('link3_text')
    link4 = URLField('link4')
    link4_text = TextField('link4_text')
    link5 = URLField('link5')
    link5_text = TextField('link5_text')

