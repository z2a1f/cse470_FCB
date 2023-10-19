from flask import Flask, render_template, request, redirect, session, send_file, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import bcrypt
from datetime import datetime

from flask_share import Share
from werkzeug.utils import secure_filename
import os
from functools import wraps
UPLOAD_FOLDER = './static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ADMINUSER = 'admin'
ADMINPASSWORD = 'password12'


share = Share()
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


share.init_app(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/admin/login'


app.secret_key = 'secret_key'
app.app_context().push()



@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/register', methods=['Get', 'POST'])
def register():
    if request.method == 'POST':
        # handle request
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')


@app.route('/admin/login', methods=['Get', 'POST'])
def adminLogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = AdminUser.query.filter_by(username=username).first()
        print(user)
        if user:
            if password == user.password:
                login_user(user)
                next = request.args.get('next')
                print(next)
                return redirect(next or url_for('playersAdd'))
            else:
                return render_template('admin-login.html', errorMsg='Invalid Admin Credentials')
        else:
            return render_template('admin-login.html', errorMsg='Invalid Admin Credentials')
    return render_template('admin-login.html', errorMsg='')


@app.route('/login', methods=['Get', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid user')
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if session['email']:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html', user=user)

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')


@app.route('/admin/logout', methods=['GET', 'POST'])
@login_required
def adminLogout():
    logout_user()
    return redirect('/admin/login')


@app.route('/admin/players', methods=['POST', 'GET'])
@login_required
def playersAdd():
    if request.method == "POST":
        name = request.form['name']
        age = request.form['age']
        height = request.form['height']
        image = request.files['image']
        weight = request.form['weight']
        nationality = request.form['nationality']
        jersey_no = request.form['jersey_no']
        position = request.form['position']
        match_played = request.form['match_played']
        goals = request.form['goals']
        assists = request.form['assists']
        file_url = ''
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_url = filename
        new_player = Player(name=name, age=age, height=height, weight=weight,
                            jersey_no=jersey_no, position=position, imageFile=file_url, match_played=match_played, goals=goals, assists=assists)

        try:
            db.session.add(new_player)
            db.session.commit()
            return redirect('/admin/players')
        except:
            return 'An error occurred'
        pass
    else:
        all_players = Player.query.order_by(Player.created_at).all()
        return render_template("player-add.html", all_players=all_players)


@app.route('/admin/players/update/<int:id>', methods=['POST', 'GET'])
@login_required
def playerUpdate(id):
    player_to_update = Player.query.get_or_404(id)
    if request.method == "POST":
        player_to_update.name = request.form['name']
        player_to_update.age = request.form['age']
        player_to_update.height = request.form['height']
        player_to_update.weight = request.form['weight']
        player_to_update.nationality = request.form['nationality']
        player_to_update.jersey_no = request.form['jersey_no']
        player_to_update.position = request.form['position']
        player_to_update.match_played = request.form['match_played']
        player_to_update.goals = request.form['goals']
        player_to_update.assists = request.form['assists']
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            player_to_update.imageFile = filename
        try:
            db.session.commit()
            return redirect('/admin/players')
        except:
            return 'An error occurred'
    else:
        return render_template("player-update.html", player=player_to_update)


@app.route('/admin/players/delete/<int:id>')
@login_required
def playerDelete(id):
    player_to_delete = Player.query.get_or_404(id)
    try:
        db.session.delete(player_to_delete)
        db.session.commit()
        return redirect('/admin/players')
    except:
        return 'An error occurred'


@app.route('/players')
def allPlayers():
    all_players = Player.query.order_by(Player.created_at).all()
    return render_template("players.html", all_players=all_players)


@app.route('/players/<int:id>')
def playerOne(id):
    player = Player.query.get_or_404(id)
    return render_template("player-one.html", player=player)


@app.route('/team')
def team():
    return render_template("team.html")




class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    age = db.Column(db.String(200), nullable=True)
    weight = db.Column(db.String(200), nullable=True)
    height = db.Column(db.String(200), nullable=True)
    imageFile = db.Column(db.String(200), nullable=True)
    nationality = db.Column(db.String(200), nullable=True)
    jersey_no = db.Column(db.String(200), nullable=True)
    position = db.Column(db.String(200), nullable=True)
    match_played = db.Column(db.String(200), nullable=True)
    goals = db.Column(db.String(200), nullable=True)
    assists = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Player %r>' % self.id



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, email, password, name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode(
            'utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


class AdminUser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


if __name__ == "__main__":
    app.run(debug=True)
    db.create_all()
    admin = AdminUser.query.get(1)
    if admin:
        pass
    else:
        new_user = AdminUser(username=ADMINUSER, password=ADMINPASSWORD)
        db.session.add(new_user)
        db.session.commit()