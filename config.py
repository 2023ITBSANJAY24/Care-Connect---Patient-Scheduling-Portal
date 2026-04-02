"""
CareConnect Configuration with In-Memory Storage
"""

class Config:
    """Base configuration"""
    SECRET_KEY = 'careconnect-secret-key-2024'
    DEBUG = True
    
    # Email Configuration (Flask-Mail)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your-email@gmail.com'  # Change this to your email
    MAIL_PASSWORD = 'your-app-password'  # Change this to your app password

# In-memory storage
users = [
    # Admin user
    {'id': 1, 'name': 'Admin', 'email': 'sanjayadmin@gmail.com', 'password': 'admin123', 'role': 'admin'},
    # Doctor user - main doctor account
    {'id': 2, 'name': 'Dr. Main Doctor', 'email': 'doctor@gmail.com', 'password': 'doctor123', 'role': 'doctor'},
    # Doctor users (id 3-8 match doctor IDs)
    {'id': 3, 'name': 'Dr. Rajesh Kumar', 'email': 'rajesh.kumar@hospital.com', 'password': 'doctor123', 'role': 'doctor'},
    {'id': 4, 'name': 'Dr. Priya Sharma', 'email': 'priya.sharma@hospital.com', 'password': 'doctor123', 'role': 'doctor'},
    {'id': 5, 'name': 'Dr. Amit Patel', 'email': 'amit.patel@hospital.com', 'password': 'doctor123', 'role': 'doctor'},
    {'id': 6, 'name': 'Dr. Sneha Gupta', 'email': 'sneha.gupta@hospital.com', 'password': 'doctor123', 'role': 'doctor'},
    {'id': 7, 'name': 'Dr. Vikram Singh', 'email': 'vikram.singh@hospital.com', 'password': 'doctor123', 'role': 'doctor'},
    {'id': 8, 'name': 'Dr. Anjali Reddy', 'email': 'anjali.reddy@hospital.com', 'password': 'doctor123', 'role': 'doctor'},
    # Sample patient user
    {'id': 101, 'name': 'John Smith', 'email': 'john.smith@email.com', 'password': 'patient123', 'role': 'patient'},
]

doctors = [
    {'id': 1, 'name': 'Dr. Rajesh Kumar', 'specialization': 'Cardiology', 'experience': '15 years'},
    {'id': 2, 'name': 'Dr. Priya Sharma', 'specialization': 'Dermatology', 'experience': '10 years'},
    {'id': 3, 'name': 'Dr. Amit Patel', 'specialization': 'Orthopedics', 'experience': '12 years'},
    {'id': 4, 'name': 'Dr. Sneha Gupta', 'specialization': 'Pediatrics', 'experience': '8 years'},
    {'id': 5, 'name': 'Dr. Vikram Singh', 'specialization': 'Neurology', 'experience': '18 years'},
    {'id': 6, 'name': 'Dr. Anjali Reddy', 'specialization': 'Gynecology', 'experience': '14 years'},
]

# Appointments storage (empty by default - real appointments will be added by patients)
appointments = []
appointment_id_counter = 1
user_id_counter = 102
