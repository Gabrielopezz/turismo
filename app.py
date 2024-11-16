from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/turismo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Actividad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)

@app.route('/')
def index():
    actividades = Actividad.query.all()
    return render_template('index.html', actividades=actividades)

@app.route('/actividad/<int:id>')
def actividad(id):
    actividad = Actividad.query.get_or_404(id)
    return render_template('activity.html', actividad=actividad)


if __name__ == '__main__':
    app.run(debug=True)
