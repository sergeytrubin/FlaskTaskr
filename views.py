from flask import Flask, render_template, request, session, \
    flash, redirect, url_for, g, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps
from forms import AddTaskForm
import logging
from logging import Formatter, FileHandler

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    due_date = db.Column(db.String(), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)

    # def __repr__(self):
    #     #return f'<Task: {self.id} {self.name}>'


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


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Goodbye!')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or \
                request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', error=error)
        else:
            session['logged_in'] = True
            return redirect(url_for('tasks'))
    return render_template('login.html')


@app.route('/tasks/')
@login_required
def tasks():
    open_tasks = [
        dict(
            name=obj.name,
            due_date=obj.due_date,
            priority=obj.priority,
            task_id=obj.id
            ) for obj in Task.query.filter(Task.status == 1).all()
    ]

    closed_tasks = [
        dict(
            name=obj.name,
            due_date=obj.due_date,
            priority=obj.priority,
            task_id=obj.id
            ) for obj in Task.query.filter(Task.status == 0).all()
    ]

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
    name = request.form['name']
    print(name)
    date = request.form['due_date']
    print(date)
    priority = request.form['priority']
    print(priority)
    if not name or not date or not priority:
        flash("All fields are required. Please try again.")
        return redirect(url_for('tasks'))
    else:
        error = False
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
            db.session.rollback
        finally:
            db.session.close()
            flash("New entry was succesfully posted!")
        if not error:
            return redirect(url_for('tasks'))
        else:
            abort (500)


# Mark tasks as complete
@app.route('/complete/<int:task_id>')
@login_required
def complete(task_id):
    try:
        task = Task.query.filter_by(id=task_id).first()
        task.status = 0
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
        Task.query.filter_by(id=task_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        flash('The task was deleted.')
    return redirect(url_for('tasks'))


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


if __name__ == '__main__':
    app.run(host='192.168.1.173')
