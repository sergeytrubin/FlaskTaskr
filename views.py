#-----------------------------------------------------------#
#                       Imports                             #
#-----------------------------------------------------------#

from flask import Flask, render_template, request, session, \
    flash, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps
from forms import AddTaskForm, RegisterForm, LoginForm

#-----------------------------------------------------------#
#                       Config                              #
#-----------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from models import Task, User

migrate = Migrate(app, db)


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to log in first')
            return redirect(url_for('login'))
    return wrap


@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    flash('Goodbye!')
    return redirect(url_for('login'))


@app.route('/register/', methods=['GET', 'POST'])
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User(
                form.name.data,
                form.email.data,
                form.password.data,
            )
            db.session.add(new_user)
            db.session.commit()
            db.session.close()
            flash('Thanks for registering. Please login.')
            return redirect(url_for('login'))
    return render_template('register.html', form=form, error=error)


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(name=request.form['name']).first()
            if user is not None and user.password == request.form['password']:
                session['logged_in'] = True
                flash('Welcome!')
                return redirect(url_for('tasks'))
            else:
                error = 'Invalid username or password.'
        else:
            error = 'Both fields are required.'
    return render_template('login.html', form=form, error=error)


@app.route('/tasks/')
@login_required
def tasks():
    open_tasks = db.session.query(Task).filter(Task.status == 1) \
        .order_by(Task.due_date.asc())
    closed_tasks = db.session.query(Task).filter(Task.status == 0) \
        .order_by(Task.due_date.asc())
    return render_template(
        'tasks.html',
        form=AddTaskForm(request.form),
        open_tasks=open_tasks,
        closed_tasks=closed_tasks
        )

# Add new tasks
@app.route('/add/', methods=['POST'])
@login_required
def new_task():
    error = False
    form = AddTaskForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit:
            try:
                new_task = Task(
                    name=request.form['name'],
                    due_date=request.form['due_date'],
                    priority=request.form['priority'],
                    status=1
                )
                db.session.add(new_task)
                db.session.commit()
            except:
                error = True
                db.session.rollback()
            finally:
                db.session.close()
                flash("New entry was succesfully posted!")
    if not error:
        return redirect(url_for('tasks'))
    else:
        abort(500)


# Mark tasks as complete
@app.route('/complete/<int:task_id>')
@login_required
def complete(task_id):
    try:
        db.session.query(Task).filter_by(task_id=task_id).update({"status": "0"})
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        flash('The task was marked as complete.')
    return redirect(url_for('tasks'))


# Delete Tasks
@app.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    try:
        Task.query.filter_by(task_id=task_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        flash('The task was deleted.')
    return redirect(url_for('tasks'))
