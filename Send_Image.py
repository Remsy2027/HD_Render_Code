import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def send_email_with_image(email, image_path):
    Sender_Email = "viscommercecdn@gmail.com"
    Sender_Password = "ehwcpeyvtawlgmiu"
    Receiver_Email = email

    # Compose the email message
    msg = MIMEMultipart()
    msg['From'] = Sender_Email
    msg['To'] = Receiver_Email
    msg['Subject'] = 'Rendered Image'

    body = 'Hi,\n\nPlease find the attached rendered image.\n\nBest regards,\nViscommerce Team'
    msg.attach(MIMEText(body, 'plain'))

    # Attach the rendered image to the email message
    with open(image_path, 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header('Content-Disposition', 'attachment', filename="rendered_image.png")
        msg.attach(img)

    # Send the email using SMTP
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(Sender_Email, Sender_Password)
        server.send_message(msg)

    print("Email Sent")

if __name__ == "__main__":
    email = sys.argv[1]
    image_path = sys.argv[2]
    send_email_with_image(email, image_path)
