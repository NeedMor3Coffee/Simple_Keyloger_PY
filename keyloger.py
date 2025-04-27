import os
import zipfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Tạo folder logs
def create_logs_folder():
    logs_folder = "logs"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
    
    # Tạo một file log mẫu
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_folder, f"log_{timestamp}.txt")
    with open(log_file, "w") as f:
        f.write("This is a sample log file.\nCreated at: " + timestamp)
    
    return logs_folder

# Nén folder logs thành file zip
def zip_logs_folder(logs_folder):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"logs_{timestamp}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(logs_folder):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, logs_folder))
    
    return zip_filename

# Gửi email với file zip đính kèm
def send_email(zip_filename, sender_email, sender_password, receiver_email):
    # Thiết lập email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = 'Logs Backup ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Đính kèm file zip
    with open(zip_filename, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    
    encoders.encode_base64(part)
    
    part.add_header(
        'Content-Disposition',
        f'attachment; filename= {zip_filename}'
    )
    
    msg.attach(part)

    # Kết nối với Gmail SMTP server
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

def main():
    # Thông tin email (thay đổi các giá trị này)
    SENDER_EMAIL = "tsting942@gmail.com"  # Thay bằng email của bạn
    SENDER_PASSWORD = "fifr qxco bylt aolm"   # Thay bằng mật khẩu ứng dụng
    RECEIVER_EMAIL = "fustegokna@gufum.com"  # Thay bằng email người nhận

    # Tạo folder logs
    logs_folder = create_logs_folder()
    
    # Nén folder
    zip_filename = zip_logs_folder(logs_folder)
    
    # Gửi email
    send_email(zip_filename, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL)
    
    # Dọn dẹp (tùy chọn)
    # os.remove(zip_filename)
    # import shutil
    # shutil.rmtree(logs_folder)

if __name__ == "__main__":
    main()
