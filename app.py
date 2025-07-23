# app.py

import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from agents.agent_coordinator import AgentCoordinator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'documents'
ALLOWED_EXTENSIONS = {'pdf', 'pptx', 'csv', 'docx', 'txt', 'md'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Increased MAX_CONTENT_LENGTH to 200 MB (200 * 1024 * 1024 bytes)
# This helps with larger PDF files. Adjust as needed.
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024

# Initialize the AgentCoordinator
coordinator = AgentCoordinator(documents_dir=UPLOAD_FOLDER)

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Checks if the uploaded file's extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Renders the main chatbot interface."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles document uploads."""
    if 'file' not in request.files:
        logging.warning("No file part in upload request.")
        return jsonify({"status": "error", "message": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        logging.warning("No selected file in upload request.")
        return jsonify({"status": "error", "message": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(file_path)
            logging.info(f"File saved: {file_path}")
            # Process the document using the coordinator
            result = coordinator.handle_document_upload(file_path)
            return jsonify(result), 200
        except Exception as e:
            # Log the full traceback for debugging server-side errors
            logging.error(f"Error during file upload or processing for {filename}: {e}", exc_info=True)
            # Provide a more informative error message to the client
            return jsonify({"status": "error", "message": f"Error processing file '{filename}': {str(e)}. Please check server logs for details."}), 500
    else:
        logging.warning(f"Invalid file type uploaded: {file.filename}")
        return jsonify({"status": "error", "message": "Invalid file type"}), 400

@app.route('/chat', methods=['POST'])
def chat():
    """Handles user chat queries."""
    data = request.get_json()
    user_query = data.get('query')

    if not user_query:
        logging.warning("No query provided in chat request.")
        return jsonify({"status": "error", "message": "No query provided"}), 400

    logging.info(f"Received chat query: {user_query}")
    try:
        response = coordinator.handle_chat_query(user_query)
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Error during chat query processing for query '{user_query}': {e}", exc_info=True)
        return jsonify({"status": "error", "message": f"Error processing query: {str(e)}. Please check server logs for details."}), 500

@app.route('/clear_data', methods=['POST'])
def clear_data():
    """Clears all indexed data and uploaded documents."""
    try:
        coordinator.clear_all_data()
        logging.info("All data cleared successfully.")
        return jsonify({"status": "success", "message": "All data cleared."}), 200
    except Exception as e:
        logging.error(f"Error clearing data: {e}", exc_info=True)
        return jsonify({"status": "error", "message": f"Error clearing data: {str(e)}"}), 500

if __name__ == '__main__':
    # Run the Flask app
    # In a production environment, use a more robust WSGI server like Gunicorn
    app.run(debug=True, host='0.0.0.0', port=5000)
