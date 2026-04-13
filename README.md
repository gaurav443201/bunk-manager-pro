# Bunk Manager Pro

A modern, full-stack educational web application designed to help students track their attendance and manage their bunks effectively. Built with Flask, MySQL, and Tailwind CSS.

## 🎯 Features
- **User Authentication:** Secure login and registration with hashed passwords.
- **Modern Dashboard:** Track your attendance dynamically.
- **Bunk Logic:** Accurately tells you how many classes you can afford to bunk while staying above 75%.
- **Recovery Logic:** Tells you how many classes you need to attend to recover below-75% attendance.
- **Quick Logging:** One-click buttons to mark "Attended" or "Bunked".
- **Visual Analytics:** Interactive Chart.js breakdown of your subjects.
- **Dark Mode Support:** Smooth dark mode experience.
- **Responsive UI:** Built with Tailwind CSS and Alpine.js for a seamless experience on mobile and desktop.

## 🚀 Setup Instructions

1. **Install Python & MySQL:**
   Ensure you have Python 3.8+ and a MySQL Server running on your system.

2. **Create a Virtual Environment (Optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Configuration:**
   - Open MySQL Workbench / CLI.
   - Run the script located in `database.sql` to create the `bunk_manager` database and the `users` and `subjects` tables.
   - **Important:** Open `app.py` and modify the `DB_CONFIG` dictionary to match your MySQL user and password (by default, user is 'root' and password is '').

5. **Run the Application:**
   ```bash
   python app.py
   ```
   
6. **Access the Web App:**
   Open your browser and navigate to `http://localhost:5000/`.

## 🛠️ Testing
If you would like to run tests, you can use `pytest`. Ensure `pytest` is installed and create a simple `tests.py` file testing the Flask HTTP responses.

## 💻 Tech Stack
- Frontend: HTML5, Tailwind CSS, Alpine.js, Chart.js, FontAwesome
- Backend: Python, Flask, Werkzeug Addons (Security, Passwords)
- Database: MySQL (mysql-connector-python)

---

## ☁️ Deployment Guide (Render)

Deploying to Render requires a Web Service and a separate remote SQL database (Render natively offers PostgreSQL, but for this project we use MySQL, so you will need a 3rd party host like Aiven, TiDB, or Railway for your MySQL backend if you are completely cloudy).

### 1. Database Setup
1. Create a free MySQL database on a provider like **Aiven**, **TiDB Free Tier**, or **Railway**.
2. Run the `database.sql` script on your newly created remote database to generate the tables.
3. Keep note of the Host, User, Password, Database Name, and Port.

### 2. Render Web Service Deployment
1. Create a [Render](https://render.com) account and connect your GitHub/GitLab.
2. Push this project to your GitHub repository.
3. On Render's dashboard, click **"New"** -> **"Web Service"**.
4. Select your repository.
5. In the settings, configure the following:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app` (This uses Gunicorn as the production WSGI server).
6. Expand **Advanced** -> **Environment Variables** and add:
   - `SECRET_KEY` = (generate a random string)
   - `DB_HOST` = (your remote database host URL)
   - `DB_USER` = (your database username)
   - `DB_PASSWORD` = (your database password)
   - `DB_NAME` = `bunk_manager` (or whatever your DB config specifies)
   - `DB_PORT` = `3306` (or provided port by your host)

7. Click **Create Web Service**. 
8. Render will build and deploy the app! You'll receive a live `.onrender.com` URL.
