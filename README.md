# Women Safety Project

This is a Django-based Women Safety Project that integrates Camera features such as screenshot capture, audio detection, weapon detection, camera location tracking, and more.

## Features
- **Screenshot Capture** 📸
- **Weapon Detection** 🔫
- **Audio Detection** 🎤
- **Camera Location Tracking** 📍
- **Camera-Based Location Detection** 🌍

## Prerequisites
- Python 3.10
- Django 5.2
- MariaDB (or MySQL)
- XAMPP (Optional for Apache Server)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/ankita12345678910/womensafety
cd womensafety
```

### 2. Create a Virtual Environment
```bash
python3.10 -m venv safe_env
source safe_env/bin/activate  # On macOS/Linux
safe_env\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create Database
Log in to your MySQL/MariaDB and create a database manually:
```sql
CREATE DATABASE womensafety;
```

### 5. Configure `.env` File
Create a `.env` file in the project root and configure database settings:
```
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_NAME=womensafety
DATABASE_USER=root
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=3306
```

### 6. Apply Migrations
```bash
python manage.py migrate
```
### 7. Run the Server
```bash
python manage.py runserver
```

## Usage
- Open `http://127.0.0.1:8000/` in your browser.
- Log in as an admin to manage users, cameras, and threats.


