from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from passlib.hash import bcrypt  # Usamos bcrypt para el hash de contraseñas
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración de la app Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización de la base de datos y el sistema de login
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Definición del modelo de usuario
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    favorites = db.relationship('Favorite', backref='user', lazy=True)


# Definición del modelo de actividad
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    favorites = db.relationship('Favorite', backref='activity', lazy=True)


# Definición del modelo de favoritos (relación entre usuario y actividad)
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)


# Cargar el usuario por su ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Ruta para la página principal
@app.route('/')
def index():
    activities = Activity.query.all()  # Obtener todas las actividades
    return render_template('index.html', activities=activities)


# Ruta para la página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user:
            # Verificamos la contraseña hasheada
            if bcrypt.verify(password, user.password):  # Usamos bcrypt para verificar la contraseña
                login_user(user)
                flash('Inicio de sesión exitoso!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Usuario o contraseña incorrectos', 'error')
        else:
            flash('Usuario no encontrado', 'error')

    return render_template('login.html')


# Ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('index'))


# Ruta para el registro de usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('El nombre de usuario ya existe', 'error')
        else:
            # Hasheamos la contraseña con bcrypt
            hashed_password = bcrypt.hash(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registro exitoso! Por favor inicia sesión', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')


# Ruta para ver los detalles de una actividad
@app.route('/activity/<int:id>')
def activity(id):
    activity = Activity.query.get_or_404(id)
    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = Favorite.query.filter_by(user_id=current_user.id, activity_id=id).first() is not None
    return render_template('activity.html', activity=activity, is_favorite=is_favorite)


# Ruta para agregar o quitar una actividad de los favoritos
@app.route('/toggle_favorite/<int:activity_id>', methods=['POST'])
@login_required
def toggle_favorite(activity_id):
    favorite = Favorite.query.filter_by(user_id=current_user.id, activity_id=activity_id).first()
    if favorite:
        db.session.delete(favorite)
        flash('Actividad eliminada de favoritos', 'info')
    else:
        new_favorite = Favorite(user_id=current_user.id, activity_id=activity_id)
        db.session.add(new_favorite)
        flash('Actividad agregada a favoritos', 'success')
    db.session.commit()
    return redirect(url_for('activity', id=activity_id))


# Ruta para ver todas las actividades favoritas del usuario
@app.route('/favorites')
@login_required
def favorites():
    favorite_activities = Activity.query.join(Favorite).filter(Favorite.user_id == current_user.id).all()
    return render_template('favorites.html', activities=favorite_activities)


# Inicializar la base de datos al arrancar la aplicación
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
