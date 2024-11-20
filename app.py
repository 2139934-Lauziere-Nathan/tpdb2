from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
from dotenv import load_dotenv
#utiliser pour hasher et verifier les mot de passe
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT')
db = mysql.connector.connect(user=db_user, password=db_password,host=db_host, database=db_name)


    
#reccupert le nom des enum pour avoir les type de croute et garniture
def recupere_valeur_enum_pizza(column):
    cursor = db.cursor()
    cursor.execute(f"SHOW COLUMNS FROM Pizza WHERE Field = '{column}'")
    result = cursor.fetchone()[1] 
    cursor.close()
    #retourne la valeur des nom d'un enum separe par une virgule
    return result.strip("enum()").replace("'", "").split(",")

#methode pour executer les query, prend en compte les parametre d'une query ansi que fetch_one et fetch_all
def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch_one:
            result = cursor.fetchone()
            cursor.fetchall()  
            return result
        if fetch_all:
            result = cursor.fetchall()
            return result
        db.commit()
    finally:
        cursor.close()
#route de la page index
@app.route('/')
def index():
    return render_template('index.html')
#route de la page de creation de client
@app.route('/client_form', methods=['GET', 'POST'])
def client_form():
    if request.method == 'POST':
        nom = request.form['nom']
        tel = request.form['tel']
        addresse = request.form['addresse']
        mdp = request.form['mdp']

        hashed_mdp = generate_password_hash(mdp)

        query = """
            INSERT INTO Client (nom, tel, addresse, mdp)
            VALUES (%s, %s, %s, %s)
        """
        execute_query(query, (nom, tel, addresse, hashed_mdp))

        client_id_query = "SELECT LAST_INSERT_ID() AS client_id"
        client_id_record = execute_query(client_id_query, fetch_one=True)
        client_id = client_id_record['client_id']

        session['client_id'] = client_id
        #dirige le client vert les option
        return redirect(url_for('options'))
    #retourne la page html de creation de client
    return render_template('creationclient.html')

#page de login pour les utilisateur
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        tel = request.form.get('tel')
        mdp = request.form.get('mdp')

        query = "SELECT mdp FROM Client WHERE tel = %s"
        hashedpass = execute_query(query, (tel,), fetch_one=True)

        if not hashedpass:
            #redirige le client a la meme page
            return redirect(url_for('login'))  

        is_valid = check_password_hash(hashedpass['mdp'], mdp) 

        if is_valid:
            #retourne le client vere la page des option
            return redirect(url_for('options'))
        else:
            #retourne le client vere la page de login
            return redirect(url_for('login'))
    return render_template('login.html')
#route de la page d'options
@app.route('/options')
def options():
    #affiche la page des options
    return render_template('options.html')
#route du formulaire de pizza
@app.route('/PizzaForm', methods=['GET', 'POST'])
def PizzaForm():
    if request.method == 'POST':
        croute = request.form['croute']
        sauces = request.form['sauces']
        garniture1 = request.form.get('garniture1', None)
        garniture2 = request.form.get('garniture2', None)
        garniture3 = request.form.get('garniture3', None)
        garniture4 = request.form.get('garniture4', None)

        pizza_query = """
            INSERT INTO Pizza (croute, sauces, garniture1, garniture2, garniture3, garniture4)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        execute_query(
            pizza_query,
            (croute, sauces, garniture1, garniture2, garniture3, garniture4)
        )

        pizza_id_query = "SELECT LAST_INSERT_ID() AS id"
        pizza_id = execute_query(pizza_id_query, fetch_one=True)['id']

        client_id = session.get('client_id')
        commande_query = """
            INSERT INTO Commande (id_client, id_pizza)
            VALUES (%s, %s)
        """
        execute_query(commande_query, (client_id, pizza_id))
        #envoie sur une page ou se message sera afficher
        return "Order submitted successfully!"

    croute_options = recupere_valeur_enum_pizza('croute')
    sauces_options = recupere_valeur_enum_pizza('sauces')
    garniture_options = recupere_valeur_enum_pizza('garniture1')
    #retourne vert le formulaire des pizza
    return render_template(
        'PizzaForm.html',
        croute_options=croute_options,
        sauces_options=sauces_options,
        garniture_options=garniture_options
    )
#route pour la liste des commande
@app.route('/liste_commande')
def liste_commande():
    query = """
    SELECT 
        liste_commande.id_commande,
        Commande.id_client,
        Commande.id_pizza,
        liste_commande.status
    FROM liste_commande
    JOIN Commande ON liste_commande.id_commande = Commande.id_commande
    ORDER BY liste_commande.id_commande DESC
    """

    liste_commande_records = execute_query(query, fetch_all=True)
    #retourne a la liste des commande
    return render_template('listecommande.html', liste_commande_records=liste_commande_records)
#route pour la page de detail des commande, requiere un id
@app.route('/commande', methods=['GET', 'POST'])
def view_commande():
    id_commande = request.args.get('id_commande') or request.form.get('id_commande')

    query = """
    SELECT 
        Commande.id_commande,
        Client.nom AS client_name,
        Client.tel AS client_tel,
        Client.addresse AS client_address,
        Pizza.croute,
        Pizza.sauces,
        Pizza.garniture1,
        Pizza.garniture2,
        Pizza.garniture3,
        Pizza.garniture4,
        liste_commande.status
    FROM Commande
    JOIN Client ON Commande.id_client = Client.id
    JOIN Pizza ON Commande.id_pizza = Pizza.id
    JOIN liste_commande ON Commande.id_commande = liste_commande.id_commande
    WHERE Commande.id_commande = %s
    """
    commande_details = execute_query(query, (id_commande,), fetch_one=True)

    if not commande_details:
        #rien trouver a cette id de commande
        return f"No details found for Commande ID {id_commande}", 404
    #retourne vert la page de description de la commande avec le id de commande
    return render_template('consulterCommande.html', commande=commande_details)

#update une commande et retourne sur la page de la commande
@app.route('/update_status', methods=['POST'])
def update_status():
    id_commande = request.form.get('id_commande')
    new_status = request.form.get('status')
    if not id_commande or not new_status:
        return "Invalid input", 400

    query = """
    UPDATE liste_commande
    SET status = %s
    WHERE id_commande = %s
    """
    execute_query(query, (new_status, id_commande))
    #retourne vert le descriptif de commande
    return redirect(url_for('view_commande', id_commande=id_commande))

if __name__ == '__main__':
    app.run(debug=True)