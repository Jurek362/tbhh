from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
# Wartość SECRET_KEY warto ustawiać np. jako zmienną środowiskową (tu domyślna wartość tylko do testów)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.db"
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "secret")
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("messages", lazy=True))

def get_or_create_admin():
    """
    Funkcja pobiera użytkownika 'admin' z bazy danych lub, jeśli nie istnieje, tworzy go.
    """
    admin_user = User.query.filter_by(name="admin").first()
    if not admin_user:
        admin_user = User(name="admin")
        db.session.add(admin_user)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("Błąd przy tworzeniu użytkownika admin:", e)
    return admin_user

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send():
    content = request.form.get("content")
    if not content or not content.strip():
        flash("Nie podałeś treści wiadomości")
        return redirect(url_for("index"))
    
    # Pobieramy lub tworzymy domyślnego użytkownika "admin"
    user = get_or_create_admin()
    
    message = Message(content=content.strip(), user=user)
    db.session.add(message)
    db.session.commit()
    
    flash("Wysłano wiadomość")
    return redirect(url_for("index"))

@app.route("/dashboard", methods=["GET"])
def dashboard():
    # Pobieramy lub tworzymy użytkownika "admin"
    user = get_or_create_admin()
    messages = Message.query.filter_by(user=user).all()
    return render_template("dashboard.html", messages=messages)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
