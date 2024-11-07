from flask import Flask, request, render_template, redirect, url_for, session, flash, send_from_directory
import pytz
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mygames.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
UPLOAD_FOLDER = os.path.join('static', 'images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gamepicture = db.Column(db.String(150))
    gamename = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(800), nullable=False)
    developer = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    releasedate = db.Column(db.String(100), nullable=False)

    comments = db.relationship('Comments', backref='game', cascade="all, delete-orphan", lazy=True)


class Comments(db.Model):
    commentid = db.Column(db.Integer, primary_key=True)
    commentatorsname = db.Column(db.String(80), nullable=False)
    comment = db.Column(db.String(800), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


@app.route('/')
def index():
    games = Game.query.all()
    games_list = [{'id': g.id, 'gamename': g.gamename, 'gamepicture': g.gamepicture} for g in games]
    return render_template("homepage.html", games=games_list)


@app.route('/display_image/<filename>')
def display_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/game/<int:game_id>')
def game_page(game_id):
    game = Game.query.get(game_id)
    if game:
        return render_template('gamepage.html', game=game)
    else:
        return "Game not found", 404


@app.route('/game/<int:game_id>/add_comment', methods=['POST'])
def add_comment(game_id):
    name = request.form.get('name')
    comment_text = request.form.get('comment')
    if not name or not comment_text:
        flash('Both name and comment are required.', 'error')
        return redirect(url_for('game_page', game_id=game_id))
    new_comment = Comments(commentatorsname=name, comment=comment_text, game_id=game_id)
    db.session.add(new_comment)
    db.session.commit()
    flash('Comment added successfully!', 'success')
    return redirect(url_for('game_page', game_id=game_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password123':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Access Denied!', 'error')
    return render_template('loginpage.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            gamename = request.form.get('gamename')
            description = request.form.get('description')
            developer = request.form.get('developer')
            publisher = request.form.get('publisher')
            releasedate = request.form.get('releasedate')

            if not (gamename and description and developer and publisher and releasedate):
                flash('All fields must be filled out, except id when adding a new game.', 'error')
                return redirect(url_for('admin'))

            if len(gamename) > 100 or len(description) > 800 or len(developer) > 100 or len(publisher) > 100:
                flash('Field lengths exceed the allowed limit', 'error')
                return redirect(url_for('admin'))

            if 'gamepicture' in request.files and request.files['gamepicture'].filename != '':
                file = request.files['gamepicture']
                filename = file.filename
                image_folder = os.path.join(app.config['UPLOAD_FOLDER'])
                if not os.path.exists(image_folder):
                    os.makedirs(image_folder)
                file_path = os.path.join(image_folder, filename)
                file.save(file_path)
            else:
                filename = 'default.jpg'

            new_game = Game(gamepicture=filename, gamename=gamename, description=description,
                            developer=developer, publisher=publisher, releasedate=releasedate)
            db.session.add(new_game)
            db.session.commit()
            flash('Game added successfully!', 'success')
            return redirect(url_for('admin'))
            pass

        elif action == 'update':
            game_id = request.form.get('id')
            game = Game.query.get(game_id)
            if not game:
                flash(f'No game found with ID {game_id}', 'error')
                return redirect(url_for('admin'))

            gamename = request.form.get('gamename')
            description = request.form.get('description')
            developer = request.form.get('developer')
            publisher = request.form.get('publisher')
            releasedate = request.form.get('releasedate')

            if len(gamename) > 100 or len(description) > 800 or len(developer) > 100 or len(publisher) > 100:
                flash('Field lengths exceed the allowed limit', 'error')
                return redirect(url_for('admin'))

            if gamename:
                game.gamename = gamename
            if description:
                game.description = description
            if developer:
                game.developer = developer
            if publisher:
                game.publisher = publisher
            if releasedate:
                game.releasedate = releasedate

            if 'gamepicture' in request.files and request.files['gamepicture'].filename != '':
                file = request.files['gamepicture']
                filename = file.filename
                image_folder = os.path.join(app.config['UPLOAD_FOLDER'])
                if not os.path.exists(image_folder):
                    os.makedirs(image_folder)
                file_path = os.path.join(image_folder, filename)
                file.save(file_path)
                game.gamepicture = filename

            db.session.commit()
            flash(f'Game with ID {game_id} updated successfully!', 'success')
            return redirect(url_for('admin'))

        elif action == 'delete':
            game_id = request.form.get('id')
            game = Game.query.get(game_id)
            if game:
                db.session.delete(game)
                db.session.commit()
                flash(f'Game with ID {game_id} deleted successfully!', 'success')
                higher_games = Game.query.filter(Game.id > game_id).all()
                for g in higher_games:
                    g.id -= 1
                db.session.commit()
            else:
                flash(f'No game found with ID {game_id}', 'error')
            return redirect(url_for('admin'))

        elif action == 'delete_comment':
            comment_id = request.form.get('commentid')
            comment = Comments.query.get(comment_id)
            if comment:
                db.session.delete(comment)
                db.session.commit()
                flash(f'Comment with ID {comment_id} deleted successfully!', 'success')
            else:
                flash(f'No comment found with ID {comment_id}', 'error')
            return redirect(url_for('admin'))

    games = Game.query.all()
    games_list = [{'id': g.id, 'gamename': g.gamename, 'gamepicture': g.gamepicture} for g in games]
    comments = Comments.query.all()
    return render_template('adminpage.html', games=games_list, comments=comments)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
