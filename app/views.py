from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import get_debug_queries
from flask.ext.babel import gettext
from app import app, db, lm, oid, babel
from forms import LoginForm, EditForm, PostForm, SearchForm, AddLink, Scraper, EditPostForm
from models import User, ROLE_USER, ROLE_ADMIN, Post, Link
from datetime import datetime
from emails import follower_notification
from guess_language import guessLanguage
from translate import microsoft_translate
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, LANGUAGES, DATABASE_QUERY_TIMEOUT, WHOOSH_ENABLED
from scraper import garconjon_scraper
from bs4 import BeautifulSoup
import urllib

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())
    
@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = get_locale()
    g.search_enabled = WHOOSH_ENABLED

@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= DATABASE_QUERY_TIMEOUT:
            app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (query.statement, query.parameters, query.duration, query.context))
    return response

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index/<int:page>', methods = ['GET', 'POST'])
def index(page = 1):
    posts = Post.query.filter().order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html',
        title = 'Home',
        posts = posts)

@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash(gettext('Invalid login. Please try again.'))
        return redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_valid_nickname(nickname)
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
        # make the user follow him/herself
        db.session.add(user.follow(user))
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    
@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
def user(nickname, page = 1):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash(gettext('User %(nickname)s not found.', nickname = nickname))
        return redirect(url_for('index'))
    posts = user.sorted_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',
        user = user,
        posts = posts)

@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        g.user.website = form.website.data
        db.session.add(g.user)
        db.session.commit()
        flash(gettext('Your changes have been saved.'))
        return redirect(url_for('edit'))
    elif request.method != "POST":
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
        form.website.data = g.user.website
    return render_template('edit.html',
        form = form)

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash(gettext('You can\'t follow yourself!'))
        return redirect(url_for('user', nickname = nickname))
    u = g.user.follow(user)
    if u is None:
        flash(gettext('Cannot follow %(nickname)s.', nickname = nickname))
        return redirect(url_for('user', nickname = nickname))
    db.session.add(u)
    db.session.commit()
    flash(gettext('You are now following %(nickname)s!', nickname = nickname))
    follower_notification(user, g.user)
    return redirect(url_for('user', nickname = nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash(gettext('You can\'t unfollow yourself!'))
        return redirect(url_for('user', nickname = nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash(gettext('Cannot unfollow %(nickname)s.', nickname = nickname))
        return redirect(url_for('user', nickname = nickname))
    db.session.add(u)
    db.session.commit()
    flash(gettext('You have stopped following %(nickname)s.', nickname = nickname))
    return redirect(url_for('user', nickname = nickname))

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    print post
    if post == None:
        flash('Post not found.')
        return redirect(url_for('index'))
    if post.author.id != g.user.id:
        flash('You cannot delete this post.')
        return redirect(url_for('index'))
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted.')
    return redirect(url_for('index'))
    
@app.route('/search', methods = ['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query = g.search_form.search.data))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
        query = query,
        results = results)

@app.route('/translate', methods = ['POST'])
@login_required
def translate():
    return jsonify({
        'text': microsoft_translate(
            request.form['text'],
            request.form['sourceLang'],
            request.form['destLang']) })

@app.route('/new_post', methods = ['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        p = Post(body = form.post.data, timestamp = datetime.utcnow(), author = g.user, image = form.image.data,
         link1 = form.link1.data, link1_text = form.link1_text.data,
         link2 = form.link2.data, link2_text = form.link2_text.data,
         link3 = form.link3.data, link3_text = form.link3_text.data,
         link4 = form.link4.data, link4_text = form.link4_text.data,
         link5 = form.link5.data, link5_text = form.link5_text.data)
        db.session.add(p)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    return render_template('new_post.html',
        form = form)

"""@app.route('/add_link/<postid>', methods = ['GET', 'POST'])
@login_required
def add_link(postid):
    form = AddLink()
    post = Post.query.filter_by(id = postid).first()
    links = Post.post_links(post)
    print post
    print links
    if form.validate_on_submit():
        l = Link(url = form.url.data, body = form.body.data, post_id = post.id)
        db.session.add(l)
        db.session.commit()
        flash('Your link is now live!')
        return redirect(url_for('add_link', postid = post.id))
    return render_template('add_link.html',
        form = form,
        post = post,
        links = links)"""

@app.route('/edit_post/<postid>', methods = ['GET', 'POST'])
@login_required
def edit_post(postid):
    form = EditPostForm()
    post = Post.query.filter_by(id = postid).first()
    if form.validate_on_submit():
        post.body = form.post.data
        post.timestamp = datetime.utcnow()
        post.author = g.user
        post.image = form.image.data
        post.link1 = form.link1.data
        post.link1_text = form.link1_text.data
        post.link2 = form.link2.data
        post.link2_text = form.link2_text.data
        post.link3 = form.link3.data
        post.link3_text = form.link3_text.data
        post.link4 = form.link4.data
        post.link4_text = form.link4_text.data
        post.link5 = form.link5.data
        post.link5_text = form.link5_text.data
        db.session.commit()
        flash('Your edits are now live!')
        return redirect(url_for('index'))
    elif request.method != "POST":
        form.image.data = post.image
        form.post.data = post.body
        form.link1.data = post.link1
        form.link1_text.data = post.link1_text
        form.link2.data = post.link2
        form.link2_text.data = post.link2_text
        form.link3.data = post.link3
        form.link3_text.data = post.link3_text
        form.link4.data = post.link4
        form.link4_text.data = post.link4_text
        form.link5.data = post.link5
        form.link5_text.data = post.link5_text
    return render_template('edit_post.html',
        form = form)

@app.route('/scraper/', methods = ['GET', 'POST'])
@login_required
def scraper():
    form = Scraper()
    url = form.url.data
    if form.validate_on_submit():
        f = urllib.urlopen(url)
        html = f.read()
        soup = BeautifulSoup(html)
        for tag in soup.findAll('a', attrs={"imageanchor" : "1"}): 
            image = tag['href']
            is_post = Post.query.filter_by(image = image).first()
            if is_post == None:
                p = Post(body = "", timestamp = datetime.utcnow(), author = g.user, image = image)
                db.session.add(p)
                db.session.commit()
    return render_template('scraper.html',
        form = form)
