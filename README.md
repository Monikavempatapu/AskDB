
# 🎙️ AskDB: AI-Powered Natural Language to SQL Voice Assistant

**AskDB** is an AI-powered voice and text-based assistant that lets you query your database using **natural language**. Whether you're working with SQLite, CSV, or Excel files — just **type or speak** your question, and AskDB will generate the correct SQL, run it, and show you the results in a beautiful interface.

This project is ideal for students, data beginners, and professionals who want a faster, easier way to work with databases.

---

## 🌟 Features

- 🎤 Voice and text input for queries
- 🤖 Converts natural language to SQL using AI
- 📁 Supports `.db`, `.csv`, and `.xlsx` files
- 🖥️ GUI interface built with Python Tkinter
- 🌙 Dark mode toggle
- 📊 Graph view (bar & pie charts)
- 💾 Export results to CSV
- 🔐 Login and Sign-Up functionality
- ✅ Error handling and validations

---

## 📋 Prerequisites

- Python 3.8 or later  
- Internet connection (for AI SQL generation)  
- Git (optional, for pushing to GitHub)  
- Required Python libraries below

---

## 📦 Required Python Libraries

Create a `requirements.txt` or install manually:

```bash
pip install openai pandas matplotlib pyttsx3 SpeechRecognition pyaudio tk
```

> ⚠ If `pyaudio` fails on Windows:
```bash
pip install pipwin
pipwin install pyaudio
```

---

## 📁 Folder Structure

```
AskDB/
│
├── gui.py             → Main GUI application
├── nl2sql.py          → Natural language to SQL logic
├── login.py           → Login logic
├── signup.py          → Signup logic
├── create_user.py     → Creates user database
├── view_user.py       → Admin view of users
├── test_load.py       → Load external files
├── schema.sql         → SQL schema (optional)
├── users.db           → User login database
├── database.db        → Sample SQLite DB
├── requirements.txt   → Dependency list
├── README.md          → Project documentation
└── venv/              → Virtual environment (optional)
```

---

## ⚙️ Setup Instructions

### ✅ 1. Clone the Project

```bash
git clone https://github.com/yourusername/AskDB.git
cd AskDB
```

### ✅ 2. Create a Virtual Environment (Optional)

```bash
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # macOS/Linux
```

### ✅ 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### ✅ 4. Create the SQLite Database (Optional)

If using `schema.sql`:

```bash
python create_user.py
python -c "import sqlite3; exec(open('schema.sql').read())"
```

---

## ▶️ How to Run AskDB

```bash
python gui.py
```

---

## 🧑‍💻 How to Use

1. 🔐 **Login or Sign up** as a new user
2. 📂 **Load a database** (.db, .csv, or .xlsx)
3. 🗣️ **Type or speak** a query like:
   - "Show all students with marks above 80"
   - "List students with grade A"
4. ⚡ **Click Generate** to convert into SQL
5. 📈 View results in **table or chart**
6. 💾 Click **Export** to save as CSV
7. 🌗 Use **Dark Mode** for night-friendly UI

---

## 📸 Screenshots & Demo Recording

- 📷 Screenshot: `Windows + Shift + S`
- 🎥 Screen recording: `Windows + Alt + R` (Game Bar)

You can add screenshots or a video demo here.

---

## 🚀 Future Enhancements

- 🌐 Web-based version (HTML/CSS UI)
- 🧠 Smarter AI queries with memory
- 🗃️ MySQL/PostgreSQL support
- 🧾 Query history and logs
- 🔊 Voice output of results

---

## 📜 License

This project is licensed under the **MIT License** – free for personal and academic use.

---

## 🙋‍♀️ Author

**Monika Vempatapu**  
Final Year Computer Engineering Project  
Made with ❤️ to simplify database interaction through AI
