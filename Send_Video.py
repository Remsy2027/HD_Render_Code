import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_email_with_video(email, video_path):
    Sender_Email = "viscommercecdn@gmail.com"
    Sender_Password = "ehwcpeyvtawlgmiu"
    Receiver_Email = email

    # Compose the email message
    msg = MIMEMultipart()
    msg['From'] = Sender_Email
    msg['To'] = Receiver_Email
    msg['Subject'] = 'Rendered Video'

    body = 'Hi,\n\nPlease find the attached rendered video.\n\nBest regards,\nViscommerce Team'
    msg.attach(MIMEText(body, 'plain'))

    # Attach the rendered video to the email message
    with open(video_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="rendered_video.mp4"')
        msg.attach(part)

    # Send the email using SMTP
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(Sender_Email, Sender_Password)
        server.send_message(msg)

    print("Email Sent")

if __name__ == "__main__":
    email = sys.argv[1]
    video_path = sys.argv[2]
    send_email_with_video(email, video_path)
