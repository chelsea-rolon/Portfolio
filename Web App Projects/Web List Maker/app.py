from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///web_list_maker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
from routes import *

with app.app_context():
    db.create_all()
    inspector = inspect(db.engine)
    if "task" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("task")}
        if "completed" not in columns:
            db.session.execute(text("ALTER TABLE task ADD COLUMN completed BOOLEAN NOT NULL DEFAULT 0"))
            db.session.commit()
        if "details" not in columns:
            db.session.execute(text("ALTER TABLE task ADD COLUMN details VARCHAR(300)"))
            db.session.commit()
        if "due_date" not in columns:
            db.session.execute(text("ALTER TABLE task ADD COLUMN due_date DATE"))
            db.session.commit()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)