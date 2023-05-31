import tkinter as tk
from tkinter import filedialog, ttk, simpledialog, messagebox
import hashlib
from cryptography.fernet import Fernet
import os
import subprocess
import time
import json
import pyperclip
from tkinter import scrolledtext

# Function to select a file
def select_file():
    filename = filedialog.askopenfilename()
    return filename

# Function to compute hash
def compute_hash(file):
    hasher = hashlib.sha256()
    with open(file, 'rb') as f:
        buffer = f.read()
        while len(buffer) > 0:
            hasher.update(buffer)
            buffer = f.read()
    hash_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.basename(file) + '.hash')
    with open(hash_file, 'w') as f:
        f.write(hasher.hexdigest())
    return hash_file

# Function to encrypt a file
def encrypt_file(file):
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    with open(file, 'rb') as f:
        data = f.read()
    cipher_text = cipher_suite.encrypt(data)
    encrypted_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.basename(file) + '.encrypted')
    with open(encrypted_file, 'wb') as f:
        f.write(cipher_text)
    key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.basename(file) + '.key.txt')
    with open(key_file, 'wb') as f:
        f.write(key)
    return encrypted_file, key_file

# Function to decrypt a file
def decrypt_file(file, key):
    cipher_suite = Fernet(key)
    with open(file, 'rb') as f:
        cipher_text = f.read()
    plain_text = cipher_suite.decrypt(cipher_text)
    decrypted_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.basename(file) + '.decrypted')
    with open(decrypted_file, 'wb') as f:
        f.write(plain_text)
    return decrypted_file

# Function to retrieve encryption keys
def get_encryption_keys():
    data = load_data()
    keys = data.get('keys', {})
    encrypted_files = [file for file in os.listdir() if file.endswith('.encrypted')]
    for encrypted_file in encrypted_files:
        file_name = os.path.splitext(encrypted_file)[0]
        key_file = file_name + '.key.txt'
        if key_file in keys:
            continue
        key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), key_file)
        if os.path.isfile(key_path):
            with open(key_path, 'rb') as f:
                key = f.read()
            keys[file_name] = key
        else:
            keys[file_name] = 'N/A'
    return keys

# Function to save keys and encryption history to a JSON file
def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f)

# Function to load keys and encryption history from the JSON file
def load_data():
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {}

# Function to open the login window
def open_login_window():
    login_window = tk.Toplevel(root)
    login_window.title('Admin Login')

    # Function to verify the password
    def verify_password():
        password = password_entry.get()

        # Verify the password here (e.g., compare with a stored password hash)
        # For simplicity, we'll use a hardcoded password "admin123" for demonstration purposes
        if password == "admin123":
            login_window.destroy()
            open_admin_window()
        else:
            messagebox.showerror('Error', 'Invalid password')

    # Label and entry for password
    password_label = tk.Label(login_window, text='Password:')
    password_label.pack(pady=10)
    password_entry = tk.Entry(login_window, show='*')
    password_entry.pack(pady=5)

    # Button to verify the password
    login_button = tk.Button(login_window, text='Login', command=verify_password)
    login_button.pack(pady=10)

# Function to open the admin window
def open_admin_window():
    admin_window = tk.Toplevel(root)
    admin_window.title('Admin Interface')

    keys = get_encryption_keys()

    # Function to copy the selected key to clipboard
    def copy_key_to_clipboard():
        selected_item = tree.focus()
        if selected_item:
            selected_key = tree.item(selected_item)['values'][0]
            pyperclip.copy(selected_key)
            messagebox.showinfo('Success', 'Key copied to clipboard')

    # Create a treeview widget to display the keys
    tree = ttk.Treeview(admin_window, columns=('Key'))
    tree.heading('#0', text='File Name')
    tree.heading('Key', text='Key')

    for file_name, key in keys.items():
        tree.insert('', 'end', text=file_name, values=(key))

    tree.pack(pady=20)

    # Button to copy the selected key to clipboard
    copy_button = tk.Button(admin_window, text='Copy Key', command=copy_key_to_clipboard)
    copy_button.pack(pady=10)

    # Save keys and encryption history when the admin window is closed
    def save_data_on_close():
        keys = get_encryption_keys()
        data = load_data()
        data['keys'] = keys
        save_data(data)

    admin_window.protocol('WM_DELETE_WINDOW', save_data_on_close)

# Function to handle button click
def handle_click():
    filename = select_file()
    if filename:
        progress_bar['value'] = 20
        root.update_idletasks()
        time.sleep(1)

        if var.get() == 'Hash':
            result = compute_hash(filename)
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, 'Hash: ' + result)
            pyperclip.copy(result)
        elif var.get() == 'Encrypt':
            result, key = encrypt_file(filename)
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, 'Encrypted file: ' + result + '\nKey: ' + key)
            pyperclip.copy(result + '\n' + key)
        elif var.get() == 'Decrypt':
            key = simpledialog.askstring("Input", "Enter decryption key:", parent=root)
            result = decrypt_file(filename, key.encode())
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, 'Decrypted file: ' + result)
            pyperclip.copy(result)
        else:
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, 'Please select a valid operation')

        progress_bar['value'] = 100

# Function to open file location
def open_file_location():
    directory = os.path.dirname(os.path.abspath(__file__))
    subprocess.Popen(f'explorer {os.path.realpath(directory)}')

# Function to open the admin login window
def open_admin_login_window():
    open_login_window()

# Main application window
root = tk.Tk()
root.geometry('500x500')
root.title('File Encryption, Decryption and Hashing Application')

# Label
label = tk.Label(root, text='Select an operation and then select a file:')
label.pack(pady=20)

# Dropdown menu to select operation
options = ['Hash', 'Encrypt', 'Decrypt']
var = tk.StringVar(root)
var.set(options[0])
opt = tk.OptionMenu(root, var, *options)
opt.pack(pady=20)

# Button to select file and execute operation
button = tk.Button(root, text='Select File', command=handle_click)
button.pack(pady=20)

# Progress bar
progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
progress_bar.pack(pady=20)

# ScrolledText widget to display result
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=40, height=10)
output_text.pack(pady=20)

# Button to open file location
file_button = tk.Button(root, text='Open File Location', command=open_file_location)
file_button.pack(pady=10)

# Button to open admin login window
admin_button = tk.Button(root, text='Admin', command=open_admin_login_window)
admin_button.pack(pady=10)

root.mainloop()
