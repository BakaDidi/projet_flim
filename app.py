import json
import os

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

from database_helper import get_db

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.secret_key = 'Clef'


@app.route('/')
def index():
    db = get_db()

    # Récupérer les films avec leurs acteurs
    cursor = db.execute('SELECT * FROM films')
    films = cursor.fetchall()

    films_with_acteurs_and_image = []
    for film in films:
        film_dict = dict(film)
        film_dict['acteurs'] = film['acteurs'] if film['acteurs'] else []  # Récupérer les acteurs du film
        film_dict['image_url'] = url_for('static', filename=film['image'])
        films_with_acteurs_and_image.append(film_dict)

    return render_template('home.jinja2', films=films_with_acteurs_and_image)


@app.route('/ajouter_film', methods=['GET', 'POST'])
def ajouter_film():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        titre = request.form['titre']
        description = request.form['description']
        annee = request.form['annee']
        realisation = request.form['realisation']
        producteur = request.form['producteur']
        image = request.files['image']
        acteurs = request.form.getlist('acteurs')

        if image:
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.root_path, 'static', 'images', image_filename))
        else:
            image_filename = None

        db = get_db()
        cursor = db.cursor()

        # Convertir la liste des acteurs en chaîne JSON
        acteurs_json = json.dumps(acteurs)

        # Insérer le film dans la table "films"
        cursor.execute(
            'INSERT INTO films (titre, description, annee, realisation, producteur, image, acteurs) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (titre, description, annee, realisation, producteur, image_filename, acteurs_json)
        )

        db.commit()

    return render_template('ajouter_film.jinja2')


@app.route('/film_detail/<int:film_id>')
def film_detail(film_id):
    db = get_db()
    cursor = db.execute('SELECT * FROM films WHERE id = ?', (film_id,))
    film = cursor.fetchone()

    if film is None:
        flash('Film non trouvé.')
        return redirect(url_for('index'))

    # Désérialiser la chaîne JSON des acteurs en une liste Python
    acteurs = json.loads(film['acteurs'])

    film_dict = dict(film)
    film_dict['acteurs'] = acteurs
    film_dict['image_url'] = url_for('static', filename=film['image'])

    return render_template('detail_film.jinja2', film=film_dict)


@app.route('/supprimer_film/<int:film_id>', methods=['GET'])
def supprimer_film(film_id):
    db = get_db()
    cursor = db.execute('SELECT * FROM films WHERE id = ?', (film_id,))
    film = cursor.fetchone()

    if film is None:
        flash('Film non trouvé.')
        return redirect(url_for('index'))

    db.execute('DELETE FROM films WHERE id = ?', (film_id,))
    db.commit()

    flash('Film supprimé avec succès.')
    return redirect(url_for('index'))


@app.route('/modifier_film/<int:film_id>', methods=['GET', 'POST'])
def modifier_film(film_id):
    db = get_db()
    cursor = db.execute('SELECT * FROM films WHERE id = ?', (film_id,))
    film = cursor.fetchone()

    if film is None:
        flash('Film non trouvé.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Récupérer les données du formulaire
        titre = request.form['titre']
        description = request.form['description']
        annee = request.form['annee']
        realisation = request.form['realisation']
        producteur = request.form['producteur']
        image = request.files['image']
        acteurs = request.form.getlist('acteurs')

        if image:
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.root_path, 'static', 'images', image_filename))
        else:
            image_filename = film['image']

        # Convertir la liste des acteurs en chaîne JSON
        acteurs_json = json.dumps(acteurs)

        # Mettre à jour les données du film dans la table "films"
        cursor.execute(
            'UPDATE films SET titre = ?, description = ?, annee = ?, realisation = ?, producteur = ?, image = ?, '
            'acteurs = ? WHERE id = ?',
            (titre, description, annee, realisation, producteur, image_filename, acteurs_json, film_id)
        )

        db.commit()

        flash('Film modifié avec succès.')
        return redirect(url_for('film_detail', film_id=film_id))

    # Désérialiser la chaîne JSON des acteurs en une liste Python
    acteurs = json.loads(film['acteurs'])

    film_dict = dict(film)
    film_dict['acteurs'] = acteurs
    film_dict['image_url'] = url_for('static', filename=film['image'])

    return render_template('modifier_film.jinja2', film=film_dict)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run(debug=True)
