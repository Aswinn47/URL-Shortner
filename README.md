🔗 URL Shortener Web App
This is a simple and secure URL Shortener built with Python Flask. It allows users to register, log in, and shorten long URLs into compact, shareable links. Each shortened URL is tied to a registered user, and users can safely shorten and manage their links within their account.

✨ Features
🔐 User Authentication (Register/Login with Email & Password)
🔑 Secure Password Storage using hashing (werkzeug.security)
✂️ Shorten URLs to unique 6-character strings
🧠 Smart Handling of duplicate users and invalid inputs
📜 Flash Messages for alerts (e.g., wrong password, account exists, etc.)
💡 Clean UI with separate pages for Login, Register, and Results
✅ Built with SQLite for lightweight, easy-to-use data storage

💻 Tech Stack
Backend: Python, Flask, SQLite
Frontend: HTML, CSS (custom styling)
Authentication: Flask-Login
Password Security: Werkzeug hashing
