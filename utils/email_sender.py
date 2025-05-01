# utils/email_sender.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailSender:
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SENDER_EMAIL = 'diyabet.takip@gmail.com'
    SENDER_PASSWORD = 'your_app_password'  # Gmail için uygulama şifresi kullanın
    
    @staticmethod
    def send_email(recipient, subject, message):
        """
        E-posta gönderir.
        
        :param recipient: Alıcı e-posta adresi
        :param subject: E-posta konusu
        :param message: E-posta içeriği
        :return: Başarılıysa True, değilse False
        """
        try:
            # E-posta oluştur
            msg = MIMEMultipart()
            msg['From'] = EmailSender.SENDER_EMAIL
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Mesajı ekle
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            # SMTP sunucusuna bağlan
            server = smtplib.SMTP(EmailSender.SMTP_SERVER, EmailSender.SMTP_PORT)
            server.starttls()
            server.login(EmailSender.SENDER_EMAIL, EmailSender.SENDER_PASSWORD)
            
            # E-postayı gönder
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"E-posta gönderilirken hata oluştu: {e}")
            return False