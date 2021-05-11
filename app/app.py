from flask import Flask, render_template, session, request
import random as rd
import mysql.connector

app = Flask(__name__)
app.secret_key = '\xec\xdf\xa1\x19\xf7\x82\xb3\x81\x1b\xbeb\n"\x99\xc6.'
app.config["DEBUG"] = True
answers = []
config = {
    'host': 'db',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'plus_ou_moins'
}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        init_game()
        return render_template('index.html')
    else:
        if session['first_guess']:
            session['first_guess'] = False
            session['game_ended'] = False

        if session['game_ended']:
            save_score(request.form['name'], len(answers))
            return render_template(
                'scores.html',
                scores=get_scores()
            )

        try:
            tried_number = check_answer()
        except (AssertionError, ValueError):
            return render_template(
                'index.html',
                error="Veuillez entrer un nombre entre 1 et 100",
                answers=answers
            )

        message = compare_numbers(tried_number)
        answers.insert(0, {'tried_number': tried_number, 'result': message})

        return render_template(
            'index.html',
            message=message,
            answers=answers,
            game_ended=session['game_ended']
        )


def init_game():
    global answers
    session['number_to_find'] = rd.randint(1, 100)
    session['first_guess'] = True
    answers = []


def check_answer():
    tried_number = int(request.form['tried_number'])
    assert 0 < tried_number < 100
    return tried_number


def compare_numbers(tried_number):
    if tried_number == session['number_to_find']:
        session['game_ended'] = True
        return f'Vous avez gagné en {len(answers)} essais !'
    if tried_number > session['number_to_find']:
        return 'C\'est moins !'
    if tried_number < session['number_to_find']:
        return 'C\'est plus !'


def get_scores():
    connection = mysql.connector.connect(**config)
    mycursor = connection.cursor(dictionary=True)
    sql = 'SELECT name, score FROM scores;'
    mycursor.execute(sql)
    scores = mycursor.fetchall()
    if scores:
        scores.sort(key=lambda i: (i['score'], i['name']))
    return scores[:10]


def save_score(name, score):
    connection = mysql.connector.connect(**config)
    mycursor = connection.cursor()
    sql = 'INSERT INTO scores (name, score) VALUES (%s, %s);'
    val = (name, score)
    mycursor.execute(sql, val)
    connection.commit()


# run the app
app.run()
