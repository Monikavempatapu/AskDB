import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyttsx3
import speech_recognition as sr
import sqlite3
import csv
from nl2sql import NL2SQL
import pandas as pd
import os
import matplotlib.pyplot as plt

# ----------------- Voice Functions -------------------
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Speak your query now.")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except:
        return "Could not understand audio."

# ----------------- SQL Runner -------------------
def run_sql(sql, db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description] if cursor.description else []
        conn.close()
        return results, headers
    except Exception as e:
        return str(e), []

# ----------------- GUI State -------------------
df = None
columns = []
table_name = ""
tables = []
current_data = None

# ----------------- Handlers -------------------
def update_table_dropdown(tables):
    table_var.set(tables[0] if tables else "")
    menu = table_dropdown["menu"]
    menu.delete(0, tk.END)
    for t in tables:
        menu.add_command(label=t, command=lambda value=t: table_var.set(value))

def load_table_data(db_path, table):
    global df, columns, table_name
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    columns = list(df.columns)
    table_name = table
    df.fillna('', inplace=True)

def handle_file_select():
    global df, columns, table_name, tables, app
    file_path = filedialog.askopenfilename(
        initialdir=os.getcwd(),
        title="Select database or data file",
        filetypes=[
            ("SQLite DB", "*.db *.sqlite"),
            ("CSV File", "*.csv"),
            ("Excel File", "*.xlsx *.xls"),
            ("All Supported", "*.db *.sqlite *.csv *.xlsx *.xls"),
            ("All Files", "*.*"),
        ]
    )
    if not file_path:
        return

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(file_path)
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        columns = list(df.columns)
        tables = [table_name]
        app.last_db_path = None
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        columns = list(df.columns)
        tables = [table_name]
        app.last_db_path = None
    elif ext in [".db", ".sqlite"]:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]
        conn.close()
        if not tables:
            messagebox.showerror("Error", "No tables found in database.")
            return
        app.last_db_path = file_path
        table_name = tables[0]
        load_table_data(file_path, table_name)
    else:
        messagebox.showerror("Error", "Unsupported file format")
        return

    update_table_dropdown(tables)
    speak("Database loaded")
    messagebox.showinfo("Loaded", f"Loaded table: {table_name}")

def on_table_change(*args):
    if hasattr(app, 'last_db_path') and app.last_db_path and table_var.get():
        load_table_data(app.last_db_path, table_var.get())
    # For CSV/Excel, do nothing (df is already loaded)

def handle_voice_query():
    query = listen()
    nl_var.set(query)

def handle_generate_sql():
    global df, columns, table_name
    query = nl_var.get().strip()
    if not query:
        messagebox.showwarning("No input", "Please enter or speak a query.")
        return

    # If user input is already SQL
    if query.lower().startswith(("select", "update", "delete", "insert", "with")):
        sql_var.set(query)
    elif df is not None and columns:
        converter = NL2SQL(table_var.get(), [col.lower() for col in columns])
        try:
            sql = converter.generate_sql(query)
            sql_var.set(sql)
        except Exception as e:
            messagebox.showerror("Error", f"Query generation failed: {e}")
            sql_var.set("")
    else:
        messagebox.showerror("Error", "No data loaded.")

def handle_run_query():
    global current_data, df, columns, table_name, app
    sql = sql_var.get().strip()
    if not sql:
        messagebox.showwarning("No SQL", "Please generate or enter a SQL query.")
        return

    # Execute via pandas if using CSV/Excel
    if df is not None:
        try:
            if "where" in sql.lower():
                clause = sql.split("WHERE", 1)[1]
                clause = clause.split("ORDER BY")[0] if "ORDER BY" in clause else clause
                clause = clause.replace(";", "").strip()
                # Convert SQL '=' to pandas '==', but not for >=, <=, !=
                import re
                clause = re.sub(r'(?<![<>=!])=(?!=)', '==', clause)
                df_result = df.query(clause)
            else:
                df_result = df
            display_results(df_result)
            current_data = (list(df_result.columns), df_result.values.tolist())
            speak(f"I found {len(df_result)} result(s).")
        except Exception as e:
            messagebox.showerror("Query failed", str(e))
    # Otherwise use sqlite
    elif hasattr(app, 'last_db_path'):
        res, hdr = run_sql(sql, app.last_db_path)
        if isinstance(res, str):
            messagebox.showerror("SQL Error", res)
            return
        display_results(pd.DataFrame(res, columns=hdr))
        current_data = (hdr, res)
        speak(f"I found {len(res)} result(s).")
    else:
        messagebox.showerror("Error", "No data source to run the query.")

def display_results(df_out):
    result_tree.delete(*result_tree.get_children())
    result_tree["columns"] = list(df_out.columns)
    result_tree["show"] = "headings"
    for col in df_out.columns:
        result_tree.heading(col, text=col)
    for _, row in df_out.iterrows():
        result_tree.insert("", tk.END, values=list(row))

def export_to_csv():
    global current_data
    if not current_data:
        messagebox.showwarning("Warning", "No data to export.")
        return
    path = filedialog.asksaveasfilename(defaultextension=".csv")
    if path:
        hdr, rows = current_data
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(hdr)
            writer.writerows(rows)
        messagebox.showinfo("Exported", f"Exported to {path}")

def handle_generate_graph():
    global df, columns
    if df is None or len(columns) < 2:
        messagebox.showwarning("No Data", "Load data and run a query first.")
        return
    # Ask user to select X and Y columns
    graph_win = tk.Toplevel(app)
    graph_win.title("Select Columns for Graph")
    graph_win.geometry("350x240")
    graph_win.resizable(False, False)
    graph_win.config(bg="#f8f8f8")

    tk.Label(graph_win, text="Select X axis:", font=("Segoe UI", 12), bg="#f8f8f8").pack(pady=(20, 5))
    x_var = tk.StringVar(value=columns[0])
    x_menu = ttk.Combobox(graph_win, textvariable=x_var, values=columns, state="readonly")
    x_menu.pack(pady=5, fill="x", padx=30)

    tk.Label(graph_win, text="Select Y axis:", font=("Segoe UI", 12), bg="#f8f8f8").pack(pady=(10, 5))
    y_var = tk.StringVar(value=columns[1])
    y_menu = ttk.Combobox(graph_win, textvariable=y_var, values=columns, state="readonly")
    y_menu.pack(pady=5, fill="x", padx=30)

    def plot_graph():
        x_col = x_var.get()
        y_col = y_var.get()
        try:
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            if df[y_col].dropna().empty:
                messagebox.showerror("Graph Error", f"No numeric data found in column '{y_col}'.")
                return
            plt.figure(figsize=(8, 5))
            df.plot(kind='bar', x=x_col, y=y_col)
            plt.title(f"{y_col} by {x_col}")
            plt.tight_layout()
            plt.show()
            graph_win.destroy()
        except Exception as e:
            messagebox.showerror("Graph Error", f"Could not plot graph: {e}")

    # Use a frame to center the button
    btn_frame = tk.Frame(graph_win, bg="#f8f8f8")
    btn_frame.pack(pady=18, fill="x")
    tk.Button(btn_frame, text="Generate", bg="#00b894", fg="white", font=("Segoe UI", 11, "bold"),
              command=plot_graph).pack(pady=0, ipadx=10)

def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    bg, fg = ("#222","#eee") if dark_mode else ("#f8f8f8","#000")
    app.config(bg=bg)
    main_frame.config(bg=bg)
    btn_frame.config(bg=bg)
    for w in main_frame.winfo_children():
        try:
            w.config(bg=bg, fg=fg)
        except:
            pass
    for btn, color in button_widgets:
        btn.config(bg="#263238" if dark_mode else color, fg="#fff")
    set_treeview_style(dark_mode)

# ----------------- GUI Layout -------------------
app = tk.Tk()
app.title("🗃️ AskDB")
app.geometry("1100x750")
app.config(bg="#f8f8f8")
dark_mode = False

table_var = tk.StringVar()
nl_var = tk.StringVar()
sql_var = tk.StringVar()

# --- Navigation Bar ---
user_logged_in = [False]  # Use a mutable type to allow modification in nested functions
current_username = [None]

def show_profile():
    profile_win = tk.Toplevel(app)
    profile_win.title("Profile")
    profile_win.geometry("320x200")
    profile_win.resizable(False, False)
    profile_win.config(bg="#f8f8f8")
    tk.Label(profile_win, text="👤 Profile", font=("Segoe UI", 16, "bold"), bg="#f8f8f8", fg="#009688").pack(pady=10)
    tk.Label(profile_win, text=f"Username: {current_username[0]}", font=("Segoe UI", 12), bg="#f8f8f8").pack(pady=10)
    tk.Button(profile_win, text="Logout", bg="#e74c3c", fg="white", font=("Segoe UI", 11, "bold"),
              command=lambda: [logout(), profile_win.destroy()]).pack(pady=10)

def logout():
    user_logged_in[0] = False
    current_username[0] = None
    update_navbar()

def do_login(username):
    user_logged_in[0] = True
    current_username[0] = username
    update_navbar()

def show_login():
    login_win = tk.Toplevel(app)
    login_win.title("Login")
    login_win.geometry("300x200")
    login_win.resizable(False, False)
    login_win.config(bg="#f8f8f8")
    tk.Label(login_win, text="Login to AskDB", font=("Segoe UI", 14, "bold"), bg="#f8f8f8").pack(pady=10)
    tk.Label(login_win, text="Username:", bg="#f8f8f8").pack()
    username = tk.Entry(login_win)
    username.pack()
    tk.Label(login_win, text="Password:", bg="#f8f8f8").pack()
    password = tk.Entry(login_win, show="*")
    password.pack()
    def do_login_and_close():
        do_login(username.get() or "User")
        login_win.destroy()
    tk.Button(login_win, text="Login", bg="#009688", fg="white", font=("Segoe UI", 11, "bold"),
              command=do_login_and_close).pack(pady=10)

def show_signup():
    signup_win = tk.Toplevel(app)
    signup_win.title("Sign Up")
    signup_win.geometry("300x250")
    signup_win.resizable(False, False)
    signup_win.config(bg="#f8f8f8")
    tk.Label(signup_win, text="Sign Up for AskDB", font=("Segoe UI", 14, "bold"), bg="#f8f8f8").pack(pady=10)
    tk.Label(signup_win, text="Username:", bg="#f8f8f8").pack()
    username = tk.Entry(signup_win)
    username.pack()
    tk.Label(signup_win, text="Password:", bg="#f8f8f8").pack()
    password = tk.Entry(signup_win, show="*")
    password.pack()
    tk.Label(signup_win, text="Confirm Password:", bg="#f8f8f8").pack()
    confirm = tk.Entry(signup_win, show="*")
    confirm.pack()
    def do_signup_and_close():
        do_login(username.get() or "User")
        signup_win.destroy()
    tk.Button(signup_win, text="Sign Up", bg="#009688", fg="white", font=("Segoe UI", 11, "bold"),
              command=do_signup_and_close).pack(pady=10)

def nav_btn_hover(e, btn, color):
    btn.config(bg=color, fg="#fff", font=("Segoe UI", 12, "bold", "underline"))

def nav_btn_leave(e, btn):
    btn.config(bg="#00b894", fg="#fff", font=("Segoe UI", 12, "bold"))

def askdb_hover(e):
    askdb_label.config(fg="#fff", font=("Segoe UI", 22, "bold", "underline"))

def askdb_leave(e):
    askdb_label.config(fg="#263238", font=("Segoe UI", 20, "bold"))

def update_navbar():
    # Remove all widgets from nav except AskDB label
    for widget in nav.winfo_children():
        if widget != askdb_label:
            widget.destroy()
    if user_logged_in[0]:
        profile_btn = tk.Label(nav, text=f"👤 {current_username[0]}", font=("Segoe UI", 12, "bold"),
                               bg="#00b894", fg="#fff", cursor="hand2", padx=18, pady=8)
        profile_btn.pack(side="right", padx=(0, 10))
        profile_btn.bind("<Button-1>", lambda e: show_profile())
        profile_btn.bind("<Enter>", lambda e: nav_btn_hover(e, profile_btn, "#009688"))
        profile_btn.bind("<Leave>", lambda e: nav_btn_leave(e, profile_btn))
    else:
        login_btn = tk.Label(nav, text="Login", font=("Segoe UI", 12, "bold"),
                             bg="#00b894", fg="#fff", cursor="hand2", padx=18, pady=8)
        login_btn.pack(side="right", padx=(0, 10))
        login_btn.bind("<Button-1>", lambda e: show_login())
        login_btn.bind("<Enter>", lambda e: nav_btn_hover(e, login_btn, "#009688"))
        login_btn.bind("<Leave>", lambda e: nav_btn_leave(e, login_btn))

        signup_btn = tk.Label(nav, text="Sign Up", font=("Segoe UI", 12, "bold"),
                              bg="#00b894", fg="#fff", cursor="hand2", padx=18, pady=8)
        signup_btn.pack(side="right", padx=(0, 10))
        signup_btn.bind("<Button-1>", lambda e: show_signup())
        signup_btn.bind("<Enter>", lambda e: nav_btn_hover(e, signup_btn, "#009688"))
        signup_btn.bind("<Leave>", lambda e: nav_btn_leave(e, signup_btn))

# --- Clean Nav Bar with Clear AskDB ---
nav = tk.Frame(app, bg="#00b894", height=64, highlightbackground="#009688", highlightthickness=2)
nav.pack(fill="x")

askdb_label = tk.Label(nav, text="🗃️ AskDB", font=("Segoe UI", 20, "bold"),
                       bg="#00b894", fg="white", padx=30, pady=10)
askdb_label.pack(side="left")
askdb_label.bind("<Enter>", askdb_hover)
askdb_label.bind("<Leave>", askdb_leave)

update_navbar()

# --- Main Content ---
main_frame = tk.Frame(app, bg=app["bg"])
main_frame.pack(fill="both", expand=True, padx=20, pady=10)

table_dropdown = tk.OptionMenu(main_frame, table_var, "")
table_dropdown.pack(anchor="w")
table_var.trace("w", on_table_change)

tk.Label(main_frame, text="Natural Language Query:", font=("Segoe UI", 14, "bold"), bg=app["bg"]).pack(anchor="w")
tk.Entry(main_frame, textvariable=nl_var, width=85, font=("Segoe UI",11)).pack(ipady=4, pady=4)

btn_frame = tk.Frame(main_frame, bg=app["bg"])
btn_frame.pack(pady=10)

def style_button(btn, color):
    btn.config(bg=color, fg="white", font=("Segoe UI",11), padx=12, pady=4, relief="flat", cursor="hand2", activebackground="#26a69a")
    btn.bind("<Enter>", lambda e: btn.config(bg="#26a69a"))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))

buttons = [
    ("📁 Choose File", handle_file_select, "#455a64"),
    ("🎙️ Speak", handle_voice_query, "#43a047"),
    ("⚙️ Generate SQL", handle_generate_sql, "#0288d1"),
    ("▶️ Run SQL", handle_run_query, "#7b1fa2"),
    ("📤 Export CSV", export_to_csv, "#f57c00"),
    ("📊 Generate Graph", handle_generate_graph, "#00b894"),
    ("🌓 Dark Mode", toggle_dark_mode, "#263238"),
]
button_widgets = []
for txt, cmd, col in buttons:
    b = tk.Button(btn_frame, text=txt, command=cmd)
    style_button(b, col)
    b.pack(side="left", padx=6)
    button_widgets.append((b, col))

tk.Label(main_frame, text="Generated SQL Query:", font=("Segoe UI",14,"bold"), bg=app["bg"]).pack(anchor="w", pady=(10,2))
tk.Entry(main_frame, textvariable=sql_var, width=85, font=("Segoe UI",11)).pack(ipady=4, pady=4)

style = ttk.Style()
style.theme_use("clam")
result_frame = tk.Frame(main_frame, bg=app["bg"])
result_frame.pack(fill="both", expand=True)

result_tree = ttk.Treeview(result_frame)
# Create vertical and horizontal scrollbars
scroll_y = ttk.Scrollbar(result_frame, orient="vertical", command=result_tree.yview)
scroll_x = ttk.Scrollbar(result_frame, orient="horizontal", command=result_tree.xview)
result_tree.configure(yscroll=scroll_y.set, xscroll=scroll_x.set)
scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")
result_tree.pack(side="left", fill="both", expand=True)

def set_treeview_style(dark):
    bg = "#263238" if dark else "#f8f8f8"
    fg = "#fff" if dark else "#000"
    style.configure("Treeview", background=bg, fieldbackground=bg, foreground=fg)
    style.configure("Treeview.Heading", background="#009688", foreground="#fff")
set_treeview_style(False)

status_bar = tk.Label(app, text="Ready", bd=1, relief="sunken", anchor="w", bg="#dfe6e9", font=("Segoe UI",9))
status_bar.pack(side="bottom", fill="x")

app.mainloop()
