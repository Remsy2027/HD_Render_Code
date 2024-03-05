from flask import Flask, request, jsonify
import subprocess
import os
from queue import Queue
from threading import Thread
from flask_cors import CORS
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app, origins=["*"])
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Create a queue to hold the GLB file requests
image_request_queue = Queue()
livingroom_image_request_queue = Queue()
video_request_queue = Queue()

def render_worker(queue, script_name):
    while True:
        email, file_path, file_data, image_text = queue.get()
        # Save the GLB file to the temporary file path on the server
        with open(file_path, 'wb') as f:
            f.write(file_data)
        # Execute the appropriate script with the email as an argument
        subprocess.Popen(['bash', script_name, email, str(image_text)])
        # Send an email notification to the user
        send_notification_email(email, 'GLB file received and added to the queue for rendering')
        queue.task_done()

# Function to send an email notification
def send_notification_email(email, message):
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SMTP_USERNAME = 'viscommercecdn@gmail.com'
    SMTP_PASSWORD = 'ehwcpeyvtawlgmiu'
    SENDER_EMAIL = 'viscommercecdn@gmail.com'

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = email
    msg['Subject'] = 'GLB Rendering Notification'
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, email, msg.as_string())
        server.quit()
        print("Email notification sent successfully")
    except Exception as e:
        print(f"Error sending email notification: {str(e)}")

# Start the image rendering worker thread
image_worker_thread = Thread(target=render_worker, args=(image_request_queue, 'Render_Image.sh'))
image_worker_thread.daemon = True
image_worker_thread.start()

# Start the image rendering worker thread
livingroom_image_worker_thread = Thread(target=render_worker, args=(livingroom_image_request_queue, 'LivingRoom_Render_Image.sh'))
livingroom_image_worker_thread.daemon = True
livingroom_image_worker_thread.start()

# Start the video rendering worker thread
video_worker_thread = Thread(target=render_worker, args=(video_request_queue, 'Render_Video.sh'))
video_worker_thread.daemon = True
video_worker_thread.start()

@app.route('/', methods=['GET'])
def index():
    return "Welcome to the GLB Upload and Rendering Service"

@app.route('/send_email', methods=['POST'])
def send_email():
    email = request.form.get('email')

    if not email:
        return 'Email not provided', 400

    # Add the email to the queue for processing by the appropriate worker thread
    request_queue.put((email, '', ''))

    return 'Rendering started. The image or video will be sent to {}'.format(email)

@app.route('/image_render', methods=['POST'])
def image_render():
    email = request.form.get('email')
    print(email)
    
    image_text = request.args.get('image_text',type=float)  # Get the image_text parameter from the URL query parameters
    print(image_text)
    
    glb_file = request.files['glbData']

    # Get the binary data of the GLB file
    file_data = glb_file.read()

    # Save the GLB file to a temporary file path on the server
    temp_file_path = os.path.join('Assets/GLB_Files', f'{email}.glb')

    # Add the request to the image rendering queue for processing by the image worker thread
    image_request_queue.put((email, temp_file_path, file_data, image_text))

    return jsonify({'message': 'GLB file received and added to the queue for image rendering'}), 200

@app.route('/livingroom_image_render', methods=['POST'])
def livingroom_image_render():
    email = request.form.get('email')
    print(email)

    image_text = request.args.get('image_text',type=float)  # Get the image_text parameter from the URL query parameters
    print(image_text)

    glb_file = request.files['glbData']

    # Get the binary data of the GLB file
    file_data = glb_file.read()

    # Save the GLB file to a temporary file path on the server
    temp_file_path = os.path.join('Assets/GLB_Files', f'{email}.glb')

    # Add the request to the image rendering queue for processing by the image worker thread
    livingroom_image_request_queue.put((email, temp_file_path, file_data, image_text))

    return jsonify({'message': 'GLB file received and added to the queue for image rendering'}), 200

@app.route('/video_render', methods=['POST'])
def video_render():
    email = request.form.get('email')
    print(email)
    
    image_text = request.args.get('image_text',type=float)  # Get the image_text parameter from the URL query parameters
    print(image_text)

    glb_file = request.files['glbData']

    # Get the binary data of the GLB file
    file_data = glb_file.read()

    # Save the GLB file to a temporary file path on the server
    temp_file_path = os.path.join('Assets/GLB_Files', f'{email}.glb')

    # Add the request to the video rendering queue for processing by the video worker thread
    video_request_queue.put((email, temp_file_path, file_data, image_text))

    return jsonify({'message': 'GLB file received and added to the queue for video rendering'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

