from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from source.controller.controller import Controller

api = Blueprint('api', __name__)

UPLOAD_FOLDER = 'static/videos'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api.route('/api/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return jsonify({'success': True, 'filename': filename, 'url': f'/static/videos/{filename}'}), 200

    return jsonify({'success': False, 'error': 'Invalid file type'}), 400

@api.route('/api/analyze_video', methods=['POST'])
def analyze_video():
    data = request.json
    required_fields = ['nome', 'cognome', 'dob', 'altezza', 'peso', 'ruolo', 'mano_dominante', 'video_filename']
    
    if not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    nome = data['nome']
    cognome = data['cognome']
    dob = data['dob']
    altezza = data['altezza']
    peso = data['peso']
    ruolo = data['ruolo']
    mano = data['mano_dominante']
    video_path = os.path.join(UPLOAD_FOLDER, data['video_filename'])

    try:
        results, percentual = Controller.onAnalize(video_path, nome, cognome, peso, altezza, dob, ruolo, mano)
        return jsonify({'success': True, 'percentuale': percentual, 'dettagli': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
