# Bunk Manager Pro

A modern, full-stack educational web application designed to help students track their attendance and manage their bunks effectively. Built with Flask, MongoDB, and Tailwind CSS.

## 🎯 Features
- **Teacher Login:** Preconfigured secure login bypass (`gaurav443201`) for presentation.
- **Modern Dashboard:** Track your attendance dynamically.
- **Bunk Logic:** Accurately tells you how many classes you can afford to bunk while staying above 75%.
- **Recovery Logic:** Tells you how many classes you need to attend to recover below-75% attendance.
- **Quick Logging:** One-click buttons to mark "Attended" or "Bunked".
- **Visual Analytics:** Interactive Chart.js breakdown of your subjects.
- **Dark Mode Support:** Smooth dark mode experience.
- **Responsive UI:** Built with Tailwind CSS and Alpine.js for a seamless experience on mobile and desktop.
- **Auto-Keep-Awake:** Pinging script prevents cloud servers from spinning down during inactivity.

## 🚀 Setup Instructions

1. **Install Python & MongoDB:**
   Ensure you have Python 3.8+ installed. You will need a MongoDB URI (either local `mongodb://localhost:27017/` or cloud via MongoDB Atlas).

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
   - The application relies on `pymongo`. It looks for an environment variable named `MONGO_URI`. 
   - If not found, it defaults to your local MongoDB server `mongodb://localhost:27017/`.

5. **Run the Application:**
   ```bash
   python app.py
   ```
   
6. **Access the Web App:**
   Open your browser and navigate to `http://localhost:5000/`. You can log in using `gaurav443201` / `443201`.

## 💻 Tech Stack
- Frontend: HTML5, Tailwind CSS, Alpine.js, Chart.js, FontAwesome
- Backend: Python, Flask, PyMongo
- Database: MongoDB

---

## ☁️ Deployment Guide (Render)

Deploying to Render requires a Web Service and a free MongoDB Atlas cloud cluster.

### 1. Database Setup
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register).
2. Create a Free Cluster (M0). 
3. Under **Network Access**, ensure you click **Allow Access From Anywhere** (`0.0.0.0/0`), otherwise Render will be blocked from connecting.
4. Go to **Database Access** and create a Database User and save the password.
5. Click **Connect** on your cluster, select **Drivers** (Python), and copy the provided `MONGO_URI` connection string.

### 2. Render Web Service Deployment
1. Create a [Render](https://render.com) account and connect your GitHub.
2. Click **"New"** -> **"Web Service"**.
3. Select your repository.
4. In the settings, configure the following:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Expand **Advanced** -> **Environment Variables** and add:
   - `SECRET_KEY` = (generate a random string)
   - `MONGO_URI` = (paste your MongoDB connection string here)
6. Click **Create Web Service**. 
7. Render will build and deploy the app! You'll receive a live `.onrender.com` URL.
