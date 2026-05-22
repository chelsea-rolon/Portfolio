from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, TextAreaField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Optional

class AddTaskForm(FlaskForm):
    title = StringField("Task Title", validators=[DataRequired()])
    due_date = DateField("Due Date", validators=[Optional()], format="%Y-%m-%d")
    details = TextAreaField("Task Details")
    submit = SubmitField("Add Task")


class EditTaskForm(FlaskForm):
    title = StringField("Task Title", validators=[DataRequired()])
    due_date = DateField("Due Date", validators=[Optional()], format="%Y-%m-%d")
    details = TextAreaField("Task Details")
    completed = BooleanField("Completed")
    submit = SubmitField("Save Task")