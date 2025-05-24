# Lost and Found Portal

A **Lost and Found Portal** web application built with **Flask** and **SQLite**. This platform allows users to register, login, report lost or found items, manage their reports, and receive notifications. It supports role-based access control with distinct roles such as student, staff, and admin.

---

## Features

### User Authentication
- Register new users with roles: **student**, **staff**, and **admin**  
- Login and logout functionality  

### Role-Based Access Control
- Only **non-admin** users (students, staff) can report lost or found items  
- **Admins** can view all reports and filter them by category  

### Report Management
- Create reports for lost or found items with:
  - Title  
  - Description  
  - Category  
  - Optional image upload  
- Edit and delete own reports  
- View reports on the user dashboard  

### Supported Categories
- Electronics  
- Mobile Phones  
- Headphones  
- Bags  
- Stationery  
- Gold  
- Belongings  

### Notifications
- Admins and users can send notifications related to reports  
- Users can view their notifications on the dashboard  

### Image Upload
- Secure upload of images for reports  
- Images are stored in `static/uploads`  

---

## Installation

### Prerequisites
- Python 3.7 or higher  
- pip package manager  

### Install Required Packages

```bash
pip install flask flask-login werkzeug
```
## Setup

### Create Upload Folder
Ensure the folder `static/uploads` exists and is writable.  
The app will automatically create it if it’s missing.

### Initialize the Database
The app initializes the SQLite database and required tables automatically on first run.

---

## Running the Application

Start the Flask server with:

```bash
python app.py
```

By default, the app runs in debug mode on:

```bash
http://127.0.0.1:5000/
```

## Usage
- Open your browser and go to http://127.0.0.1:5000/

- Register a new user and select a role (student, staff, or admin)

- Login to access the dashboard and reporting features

- Use the navigation menu to visit other pages like About, Help, and Contact
