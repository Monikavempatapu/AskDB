import customtkinter as ctk
from tkinter import messagebox
import sqlite3

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("450x400")
app.title("📝 VoiceSQL Sign Up")

def create_account():
    user = username.get()
    pwd = password.get()
    
    if not user or not pwd:
        messagebox.showwarning("Input Error", "All fields required.")
        return

    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pwd))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Account created! Please log in.")
        app.destroy()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists.")

ctk.CTkLabel(app, text="🔐 Register for VoiceSQL", font=("Segoe UI", 22, "bold")).pack(pady=30)

username = ctk.CTkEntry(app, placeholder_text="Choose username", width=250)
username.pack(pady=10)

password = ctk.CTkEntry(app, placeholder_text="Choose password", show="*", width=250)
password.pack(pady=10)

ctk.CTkButton(app, text="📥 Sign Up", command=create_account, width=200).pack(pady=20)

app.mainloop()
