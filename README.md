# Bunk Manager Pro
**Created by Gaurav Navghare**

A modern, full-stack educational web application designed to help students track their attendance and manage their bunks effectively. Built with Flask, MongoDB, and Tailwind CSS.

## 🎯 Features
- **Student Login:** Preconfigured secure login bypass (`gaurav443201`) for presentation.
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

6. Click **Create Web Service**. 
7. Render will build and deploy the app! You'll receive a live `.onrender.com` URL.
