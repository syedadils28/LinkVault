# LinkVault 🔐

A modern, highly-secure, and beautifully designed Link Management & Export Web Application built with Python Flask. Developed by **SA_Coder**.

---

## 🌟 Features

- **Link Organization**: Securely save, categorize, tag, and favorite your important URLs.
- **Interactive Landing Page**: A beautiful hero section featuring a live "Quick Add" vault demo, interactive particles, and a customized portfolio showcase.
- **Smart Categorization**: Tag, filter, and organize links dynamically.
- **Robust Exports**: Export your vault data into multiple formats including **CSV**, **Markdown**, **JSON**, and **PDF**.
- **User Authentication**: Full secure login, registration, and password reset workflows.
- **Premium UI**: Designed with glassmorphism, dynamic glowing elements, custom scrollbars, and a built-in **Light/Dark Mode** toggle.
- **Personal Notes**: Built-in Markdown editor to attach detailed notes to your saved links.

---

## 💻 Technology Stack

- **Backend**: Python 3, Flask, Flask-SQLAlchemy, Flask-Login
- **Frontend**: HTML5, Vanilla CSS, Vanilla JavaScript, FontAwesome Icons
- **Database**: SQLite (Perfect for local storage and free hosting)
- **Exporters**: pandas, ReportLab, python-docx

---

## 📂 Folder Structure

```text
Link_save_project/
├── app/
│   ├── exporters/       # Export modules (Excel, PDF, CSV, etc.)
│   ├── models/          # Database models (User, Link, Collection, Tag)
│   ├── routes/          # Application routes (Auth, Dashboard, Links)
│   ├── services/        # Business logic
│   ├── static/          # CSS, JavaScript, and Images (SA_Coder Logo)
│   └── templates/       # HTML templates
├── instance/            # SQLite database file (created automatically)
├── exports/             # Where generated export files are saved
├── tests/               # Pytest test files
├── start_app.bat        # Windows quick-start script
├── app.py               # Main Flask application entry point
├── config.py            # Configuration settings
└── requirements.txt     # Python dependencies
```

---

## 🚀 How to Setup and Run

### Method 1: The Easy Way (Windows Only)
If you are on a Windows machine, I have included a batch file that automates the entire startup process.
1. Make sure Python 3 is installed on your computer.
2. Double-click the **`start_app.bat`** file in the project folder.
3. The script will automatically activate the virtual environment, start the local server, and open your web browser to `http://127.0.0.1:5000`.

### Method 2: Manual Setup (Windows / Mac / Linux)
1. **Open your terminal** and navigate to the project folder.
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```
3. **Activate the virtual environment:**
   - **Windows:** `venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`
4. **Install all dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Run the Application:**
   ```bash
   python app.py
   ```
   *Note: The app will automatically create the `instance/site.db` SQLite database on its first run.*
6. **Access the Application:** Open your web browser and go to **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🌐 Hosting for Free (PythonAnywhere)

Since this project uses an **SQLite** database, the absolute best place to host it for free is [PythonAnywhere.com](https://www.pythonanywhere.com/) because they offer persistent file storage on their free tier.

**Steps to host:**
1. Create a free account on PythonAnywhere.
2. Open their **Bash console** and clone your GitHub repository.
3. Go to the **Web** tab and click **"Add a new web app"**.
4. Choose **Flask** and select your Python version.
5. In the **Code** section, set your Source Code directory to your repository folder.
6. Open the **WSGI configuration file** (link provided in the Web tab) and modify the import statement to:
   ```python
   from app import app as application
   ```
7. Click **Reload** on the Web tab, and your site is live!

---

Developed with ❤️ by [SA_Coder](https://sacoderportfolio.netlify.app/)
