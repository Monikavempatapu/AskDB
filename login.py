import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import subprocess
import sys
import os

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("450x420")
app.title("🔐 VoiceSQL Login")

def login():
    user = username.get()
    pwd = password.get()

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
    result = cursor.fetchone()
    conn.close()

    if result:
        messagebox.showinfo("Success", f"Welcome {user}!")
        app.destroy()

        # Launch VoiceSQL GUI
        subprocess.run([sys.executable, "gui.py"])
    else:
        messagebox.showerror("Failed", "Invalid username or password")

def open_signup():
    app.destroy()
    subprocess.run([sys.executable, "signup.py"])

# UI Layout
ctk.CTkLabel(app, text="🔑 VoiceSQL Login", font=("Segoe UI", 22, "bold")).pack(pady=30)

username = ctk.CTkEntry(app, placeholder_text="Username", width=250)
username.pack(pady=10)

password = ctk.CTkEntry(app, placeholder_text="Password", show="*", width=250)
password.pack(pady=10)

ctk.CTkButton(app, text="🔓 Login", command=login, width=200).pack(pady=15)
ctk.CTkButton(app, text="📝 Sign Up", command=open_signup, width=200, fg_color="#777").pack()

app.mainloop()
