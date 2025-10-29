# 📚 Bookstore Web App

A simple bookstore web application built using **Flask (Python)** with CSV-based data storage.  
This project displays a list of books, their details, and can be extended to support features like cart, wishlist, and authentication.

---

## 🚀 Features

- Displays a catalog of books from a CSV file  
- Shows book details (title, author, price, etc.)  
- Easy to extend for cart, wishlist, or database integration  
- Uses Flask templates (Jinja2) for dynamic rendering  
- Simple structure for beginners to understand Flask apps  

---

## 🗂️ Project Structure

bookstore/
├── app.py # Main Flask app
├── books_products.csv # Book data in CSV format
├── database_upload.py # Script to handle CSV data upload
├── execute.py # Optional runner script
├── requirements.txt # Python dependencies
├── templates/ # HTML templates (UI)
│ ├── base.html
│ ├── index.html
│ └── ...
└── static/ # Static files (CSS, images, JS)
└── images/

yaml
Copy code

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/psaipavan/bookstore.git
cd bookstore
2️⃣ Create a virtual environment (recommended)
bash
Copy code
python -m venv venv
Activate it:

Windows:

bash
Copy code
venv\Scripts\activate
macOS/Linux:

bash
Copy code
source venv/bin/activate
3️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
▶️ Run the Application
To start the Flask server:

bash
Copy code
python app.py
Then open your browser and go to:

cpp
Copy code
http://127.0.0.1:5000/
🧩 How It Works
The app reads data from books_products.csv.

Flask loads this data and displays it on the website.

Templates inside templates/ handle the design.

You can add, update, or delete books easily by editing the CSV.

🛠️ Future Enhancements
Replace CSV with pymysql

Add Login / Signup pages

Implement Cart and Checkout system

Add Search and Filter functionality

Build a REST API version of the bookstore

Improve UI with Bootstrap or React frontend

🤝 Contributing
Contributions are welcome!
If you’d like to improve this project:

Fork the repo

Create a new branch

Commit and push your changes

Open a Pull Request 🚀


👤 Author
P. Sai Pavan

GitHub: psaipavan

Email: saipavanpulluri07@gmail.com
