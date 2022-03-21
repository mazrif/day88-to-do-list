# day 88 -To do list program

# to improve - make webpage more mobile responsive, add contact me form in About, explain how to use in About, enable links to Github, Linkedin

from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import RegisterForm, LoginForm
import os


app = Flask(__name__)
Bootstrap(app)

# variables
task_list = []
delete = '✘'
registered = "You are already registered. Please log in"
empty_task = "You have not entered a task"
same_task = "You have already entered this task"

# to enable login capabilities
login_manager = LoginManager()
login_manager.init_app(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///todolist.db')
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# create User table
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    tasks = relationship('Task', back_populates='user')

# create Task table
class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    # create Foreign Key, 'user.id' relates to id of tablename 'user'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', back_populates='tasks')
    task_name = db.Column(db.String(250), nullable=False)
    date_created = db.Column(db.String(250), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    date_completed = db.Column(db.String(250))
    # this will act like a list of Task objects linked to each User


db.create_all()


# functions
def check_task(task):  # check task entered not empty or already in task_list
    if task == "":
        flash(empty_task)
        # return redirect(url_for('index'))
    elif task in task_list:
        flash(same_task)

    else:
        task_list.append(task)
    return  redirect(url_for('index'))


def check_user_task(task, date):
    tasks = Task.query.all()
    for t in tasks:
        if t.task_name == task and t.date_created == date:
            flash(same_task)
    return redirect(url_for('user_page'))


def sort_task(status):
    tasks = Task.query.all()
    completed_tasks = [task for task in tasks if task.completed == status]
    return completed_tasks


# admin_only decorator
def admin_only(f):
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__  # add this code if you want to apply decorator to multiple functions
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def index():
    date = dt.date.today().strftime("%d/%m/%Y")
    if current_user.is_authenticated:
        return redirect(url_for("user_page"))
    else:
        if request.method == "POST":
            task = request.form['task']
            check_task(task)
            return render_template('index.html', tasks=task_list, date=date)
        else:
            return render_template('index.html', tasks=task_list, date=date)


@app.route('/user', methods=['GET', 'POST'])
@login_required
def user_page():
    user = current_user
    tasks = sort_task(status=False)
    date = dt.date.today().strftime("%d/%m/%Y")
    if request.method == "POST":
        task = request.form['task']
        if task == "":
            flash(empty_task)
        # elif Task.query.filter_by(task_name=task).first():
        #   flash(same_task)

        else:
            # date = dt.date.today().strftime("%d/%m/%Y")
            check_user_task(task, date)
            new_task = Task(
                task_name=task,
                date_created=date,
                user_id=user.id,
            )
            db.session.add(new_task)
            db.session.commit()
        return redirect(url_for('user_page'))
    else:
        return render_template('user.html', user=user, user_tasks=tasks, date=date, logged_in=current_user.is_authenticated)


# register new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User()
        new_user.email = form.email.data
        if User.query.filter_by(email=new_user.email).first():
            flash(registered)
            return redirect(url_for('login'))
        else:
            unhashed_password = form.password.data
            new_user.password = generate_password_hash(unhashed_password, method='pbkdf2:sha256', salt_length=8)
            new_user.name = form.name.data
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('index', logged_in=True))
    else:
        return render_template("register.html", form=form, logged_in=current_user.is_authenticated)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# login registered user
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_email = form.email.data
        login_password = form.password.data
        try:
            user = User.query.filter_by(email=login_email).first()
            if check_password_hash(user.password, login_password):
                login_user(user)
                return redirect(url_for('user_page', logged_in=True))
            else:
                flash("Invalid password, please try again")
                return redirect(url_for('login'))
        except AttributeError:
            flash('No such email exists, please register')
            return redirect(url_for('register'))
    else:
        return render_template("login.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html')


#delete task from database
@app.route("/delete/<int:task_id>")
@login_required
def delete(task_id):
    task_to_delete = Task.query.get(task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('user_page', logged_in=True))


@app.route("/checkbox", methods=["GET", "POST"])
@login_required
def checkbox():
    selected_tasks = request.form.getlist('checked_task')
    date = dt.date.today().strftime("%d/%m/%Y")
    for i in selected_tasks:
        task_id = int(i)
        task_to_update = Task.query.get(task_id)
        task_to_update.completed = True
        task_to_update.date_completed = date
        db.session.commit()
    return redirect(url_for('user_page', logged_in=True))


@app.route("/completed_tasks")
@login_required
def completed_tasks():
    user = current_user
    tasks = sort_task(status=True)
    return render_template("view.html", user=user, tasks=tasks, logged_in=current_user.is_authenticated)





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

