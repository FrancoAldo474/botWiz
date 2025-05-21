from flask import Flask, render_template, request, redirect, url_for, session
from flask import jsonify, send_from_directory, send_file
import os
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message
from dotenv import load_dotenv

from api import api as api_blueprint
from source.controller.controller import Controller
from source.model.PDFgenEN import PDFGenerator

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Sostituisci con una chiave sicura per sessioni
app.register_blueprint(api_blueprint)

# Cartella per i file caricati
UPLOAD_FOLDER = 'static/videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
load_dotenv()

# Estensioni supportate
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_DEFAULT_SENDER=('WizShot Reviews', 'wizshotai@gmail.com')
)
mail = Mail(app)


@app.route('/send-review', methods=['POST'])
def send_review():
    data = request.json
    name   = data.get('name')
    rating = data.get('rating')
    text   = data.get('text')

    # validazione minima
    if not (name and rating and text):
        return jsonify({'error': 'Campi mancanti'}), 400

    # prepara e invia la mail
    msg = Message(
        subject='Nuova recensione WizShot',
        recipients=['wizshotai@gmail.com']
    )
    msg.body = f'''
    Hai ricevuto una nuova recensione:

    Nome: {name}
    Voto: {rating} stelle

    “{text}”
    '''
    try:
        mail.send(msg)
        return jsonify({'ok': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'video' not in request.files:
            return "No file part"
        file = request.files['video']
        if file.filename == '':
            return "No selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            session['video_filename'] = filename  # Salva il nome del file per la successiva pagina
            return redirect(url_for('upload2'))
        return "File type not allowed"
    return render_template('upload.html')

@app.route('/upload2')
def upload2():
    # Verifica se il nome del video è presente nella sessione
    if 'video_filename' not in session:
        return redirect(url_for('upload'))  # Se non c'è video, torna alla pagina di upload
    
    # Prendi il nome del video dalla sessione e mostra il video
    video_filename = session['video_filename']
    video_url = url_for('static', filename=f'videos/{video_filename}')
    return render_template('upload2.html', video_url=video_url)

@app.route('/change_video', methods=['POST'])
def change_video():
    if 'video' not in request.files:
        return {'success': False, 'error': 'No file part'}

    file = request.files['video']
    if file.filename == '':
        return {'success': False, 'error': 'No selected file'}

    if file and allowed_file(file.filename):
        # Elimina il video precedente
        old_filename = session.get('video_filename')
        if old_filename:
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_filename)
            if os.path.exists(old_path):
                os.remove(old_path)

        # Salva il nuovo video
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['video_filename'] = filename
        video_url = url_for('static', filename=f'videos/{filename}')
        return {'success': True, 'video_url': video_url}

    return {'success': False, 'error': 'Invalid file type'}

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'video_filename' not in session:
        return redirect(url_for('upload'))

    # Salva i dati nella sessione
    session['nome'] = request.form.get('nome')
    session['cognome'] = request.form.get('cognome')
    session['dob'] = request.form.get('dob')
    session['altezza'] = request.form.get('altezza')
    session['peso'] = request.form.get('peso')
    session['ruolo'] = request.form.get('ruolo')
    
    hand_d = request.form.get('dominant_hand')
    if hand_d == 'Left':
        session['mano_dominante'] = 'sinistro'
    else:
        session['mano_dominante'] = 'destro'

    return redirect(url_for('loading'))  # Vai alla pagina con loader

@app.route('/process_video', methods=['POST'])
def process_video():
    name = session.get('nome')
    surname = session.get('cognome')
    birth = session.get('dob')
    height = session.get('altezza')
    weight = session.get('peso')
    position = session.get('ruolo')
    hand = session.get('mano_dominante')
    video_path = f"static/videos/{session['video_filename']}"

    # Esegui l'analisi
    [results, percentual] = Controller.onAnalize(video_path, name, surname, weight, height, birth, position, hand)

    session['results'] = results
    session['percentual'] = percentual

    return jsonify({'success': True})

@app.route('/get_frame/<fase>')
def get_frame(fase):
    filename = session.get(fase)
    if filename:
        return send_from_directory('static/temp_frames', filename)
    else:
        return "Frame non trovato", 404

@app.route('/genera_pdf')
def genera_pdf():
    output_path = "scheda_giocatore.pdf"
    background_image = "static/images/background.png"

    

    generator = PDFGenerator(output_path, background_image)
    frasi=generator.raggruppa_frasi_per_fase(session.get('results'))
    generator.crea_pdf(
        nome = session.get('nome'),
        cognome = session.get('cognome'),
        data_nascita = session.get('dob'),
        posizione = session.get('ruolo'),
        mano_dominante = session.get('mano_dominante'),
        frasi_per_fase=frasi
    )

    # Imposta 'as_attachment=True' per forzare il download
    return send_file(output_path, as_attachment=True, download_name="scheda_giocatore.pdf")

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/choice')
def choice():
    return render_template('choice.html')

@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/perfect')
def perfect():
    return render_template('moreInfo.html')

@app.route('/advanced_analysis')
def advanced_analysis():
    return render_template('advanced_analysis.html')

@app.route('/plus_analysis')
def plus_analysis():
    return render_template('plus_analysis.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
