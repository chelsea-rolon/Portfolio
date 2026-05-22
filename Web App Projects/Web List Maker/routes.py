from app import app, db
from flask import redirect, render_template, request, url_for

import forms
from models import Task

@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
  form = forms.AddTaskForm()
  if form.validate_on_submit():
    new_task = Task(title=form.title.data, due_date=form.due_date.data, details=form.details.data)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for("home"))

  tasks = Task.query.order_by(Task.date.desc()).all()
  return render_template("home.html", form=form, tasks=tasks)


@app.route("/index", methods=["GET"])
def index_redirect():
  return redirect(url_for("home"))


@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
  task = Task.query.get_or_404(task_id)
  task.completed = not task.completed
  db.session.commit()
  return redirect(url_for("home"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
  task = Task.query.get_or_404(task_id)
  db.session.delete(task)
  db.session.commit()
  return redirect(url_for("home"))


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
  task = Task.query.get_or_404(task_id)
  form = forms.EditTaskForm(obj=task)

  if form.validate_on_submit():
    task.title = form.title.data
    task.due_date = form.due_date.data
    task.details = form.details.data
    task.completed = form.completed.data
    db.session.commit()
    return redirect(url_for("home"))

  return render_template("edit.html", form=form, task=task)

@app.route("/about")
def about():
  return render_template("about.html")
