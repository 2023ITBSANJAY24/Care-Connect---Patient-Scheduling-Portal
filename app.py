"""
CareConnect - Flask Patient Login System with SQLite Database
Complete working application with SQLAlchemy
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import config

# Import db and models from models package
from models import db, User, Doctor, Appointment, MedicalRecord

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# SQLite Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'careconnect-secret-key-2024'

# Flask-Mail Configuration with Gmail SMTP
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'careconnecthospital1@gmail.com' # Your Gmail address
app.config['MAIL_PASSWORD'] =  'raoynudnrogadlyr'  # Your Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = 'careconnecthospital1@gmail.com'

# Initialize Flask-Mail
mail = Mail(app)

# Initialize SQLAlchemy with app
db.init_app(app)


# ==================== EMAIL FUNCTION USING FLASK-MAIL ====================
def send_email(to_email, subject, body):
    try:
        msg = Message(subject, recipients=[to_email], body=body)
        mail.send(msg)
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)


# ==================== HTML PAGES ROUTES ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login-page')
def login_page():
    return render_template('login.html')

@app.route('/register-page')
def register_page():
    return render_template('register.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/patient/dashboard')
def patient_dashboard():
    # Get doctors from database
    doctors_list = Doctor.query.all()
    return render_template('patient/dashboard.html', doctors=doctors_list)

@app.route('/admin-login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/doctor-login', methods=['GET','POST'])
def doctor_login():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        doctor = Doctor.query.filter_by(email=email, password=password).first()

        if doctor:
            session['user_id'] = doctor.id
            session['role'] = 'doctor'
            session['doctor_id'] = doctor.id

            return redirect(url_for('doctor_dashboard'))
        else:
            flash("Invalid email or password")

    return render_template('doctor_login.html')

# ==================== HELPER FUNCTION TO GET DOCTOR ID ====================
def get_doctor_id_from_session():
    """Helper function to get the correct doctor_id from session"""
    # First priority: Use doctor_id stored in session during login (most reliable)
    doctor_id = session.get('doctor_id')
    
    if doctor_id:
        return doctor_id
    
    # Fallback: If not in session, try to find by other methods
    user_id = session.get('user_id')
    user_name = session.get('name', '')
    
    # Try to find the doctor in the Doctor table by matching name
    all_doctors = Doctor.query.all()
    for doc in all_doctors:
        if doc.name.lower() in user_name.lower() or doc.name == user_name:
            doctor_id = doc.id
            break
    
    # If not found by name, try to find by user_id matching doctor id
    if not doctor_id:
        doctor = Doctor.query.get(user_id)
        if doctor:
            doctor_id = doctor.id
    
    # Also check config.doctors as fallback
    if not doctor_id:
        for doc in config.doctors:
            if doc['id'] == user_id:
                doctor_id = user_id
                break
    
    # Last resort - use user_id directly
    if not doctor_id:
        doctor_id = user_id
    
    return doctor_id


# ==================== DOCTOR LOGIN API ROUTE ====================
@app.route('/doctor_login', methods=['POST'])
def doctor_login_api():
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Invalid login data'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400
    
    doctor_user = None
    
    # First check in config.users for doctor
    for user in config.users:
        if user.get('email') == email and user.get('role') == 'doctor':
            doctor_user = user
            break  # Fixed: break is now inside the if condition
    
    # If not found in config, check in database (User table)
    if not doctor_user:
        db_doctor = User.query.filter_by(email=email, role='doctor').first()
        if db_doctor and db_doctor.password == password:
            doctor_user = {
                'id': db_doctor.id,
                'name': db_doctor.name,
                'email': db_doctor.email,
                'password': db_doctor.password,
                'role': db_doctor.role
            }
    
    # Verify password
    if doctor_user and doctor_user.get('password') == password:
        # Get the actual doctor_id from Doctor table/database
        doctor_id = None
        doctor_email = doctor_user.get('email')
        
        # First try to find in database
        db_doctor = Doctor.query.filter_by(email=doctor_email).first()
        if db_doctor:
            doctor_id = db_doctor.id
        else:
            # Fallback: try to find by matching name
            doctor_name = doctor_user.get('name', '')
            for doc in config.doctors:
                if doc['name'].lower() in doctor_name.lower() or doc['name'] == doctor_name:
                    doctor_id = doc['id']
                    break
        
        # Store session data
        session['user_id'] = doctor_user.get('id')
        session['role'] = doctor_user.get('role')
        session['name'] = doctor_user.get('name')
        # Store the actual doctor_id for appointment queries
        if doctor_id:
            session['doctor_id'] = doctor_id
        
        return jsonify({
            'message': 'Login successful',
            'redirect': '/doctor/dashboard'
        }), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401


# ==================== ADMIN LOGIN API ROUTE ====================
@app.route('/admin_login', methods=['POST'])
def admin_login_api():
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Invalid login data'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400
    
    admin_user = None
    for user in config.users:
        if user.get('email') == email and user.get('role') == 'admin':
            admin_user = user
            break
    
    if admin_user and admin_user.get('password') == password:
        session['user_id'] = admin_user.get('id')
        session['role'] = admin_user.get('role')
        session['name'] = admin_user.get('name')
        return jsonify({
            'message': 'Login successful',
            'redirect': '/admin/dashboard'
        }), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401


# ==================== ADMIN DASHBOARD ROUTE ====================
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('user_id') or session.get('role') != 'admin':
        flash('Please login as admin', 'warning')
        return redirect(url_for('admin_login'))
    
    # Fetch appointments from database with doctor and patient details
    appointments_db = Appointment.query.all()
    
    # Convert to list of dicts for template
    all_appointments = []
    for appt in appointments_db:
        doctor = Doctor.query.get(appt.doctor_id)
        patient = User.query.get(appt.patient_id)
        
        appt_dict = {
            'id': appt.id,
            'patient_id': appt.patient_id,
            'patient_name': appt.patient_name or (patient.name if patient else 'Unknown'),
            'doctor_id': appt.doctor_id,
            'doctor_name': appt.doctor_name or (doctor.name if doctor else 'Unknown'),
            'specialization': appt.specialization or (doctor.specialization if doctor else 'General'),
            'date': appt.date,
            'time': appt.time,
            'symptoms': appt.symptoms,
            'status': appt.status
        }
        all_appointments.append(appt_dict)
    
    # Get all users and doctors from database for stats
    users = User.query.all() if hasattr(User, 'query') else config.users
    doctors_list = Doctor.query.all() if hasattr(Doctor, 'query') else config.doctors
    
    # Get recent appointments (latest 5)
    recent_appointments = sorted(all_appointments, key=lambda x: x['id'], reverse=True)[:5]
    
    # Get patients list (users with role='patient')
    patients_list = [u for u in users if hasattr(u, 'role') and u.role == 'patient'] if hasattr(users[0], 'role') else []
    
    # Get all medical records (consultations) for System History
    medical_records = MedicalRecord.query.all()
    patient_history = []
    doctor_history = []
    
    for record in medical_records:
        patient = User.query.get(record.patient_id)
        doctor = Doctor.query.get(record.doctor_id)
        
        # Get appointment date if exists
        appointment_date = ''
        if record.appointment_id:
            appt = Appointment.query.get(record.appointment_id)
            if appt:
                appointment_date = appt.date
        
        # Patient History entry
        patient_history.append({
            'id': record.id,
            'patient_name': patient.name if patient else 'Unknown',
            'doctor_name': doctor.name if doctor else 'Unknown',
            'appointment_date': appointment_date,
            'diagnosis': record.diagnosis or '-',
            'prescription': record.prescription or '-',
            'status': 'Completed' if record.diagnosis else 'Pending'
        })
        
        # Doctor History entry
        doctor_history.append({
            'id': record.id,
            'doctor_name': doctor.name if doctor else 'Unknown',
            'patient_name': patient.name if patient else 'Unknown',
            'consultation_date': appointment_date,
            'prescription_given': record.prescription or '-',
            'notes': record.notes or '-'
        })
    
    return render_template('admin/dashboard.html', 
                           users=users,
                           doctors=doctors_list,
                           appointments=all_appointments,
                           recent_appointments=recent_appointments,
                           patients=patients_list,
                           patient_history=patient_history,
                           doctor_history=doctor_history)


# ==================== DOCTOR DASHBOARD ROUTES ====================
@app.route('/doctor/dashboard')
def doctor_dashboard():
    if not session.get('user_id') or session.get('role') != 'doctor':
        flash('Please login as a doctor', 'warning')
        return redirect(url_for('doctor_login'))
    
    # Get the logged-in user's ID
    user_id = session.get('user_id')
    
    # First priority: Use doctor_id stored in session during login (most reliable)
    doctor_id = session.get('doctor_id')
    
    # Find the doctor_id that corresponds to this user if not in session
    # This is fallback logic for backward compatibility
    if not doctor_id:
        doctor = None
        
        # Get user info
        user_name = session.get('name', '')
        
        # Try to find the doctor in the Doctor table by matching name
        all_doctors = Doctor.query.all()
        for doc in all_doctors:
            if doc.name.lower() in user_name.lower() or doc.name == user_name:
                doctor = doc
                doctor_id = doc.id
                break
        
        # If not found by name, try to find by user_id matching doctor id
        if not doctor_id:
            doctor = Doctor.query.get(user_id)
            if doctor:
                doctor_id = doctor.id
        
        # Also check config.doctors as fallback
        if not doctor_id:
            for doc in config.doctors:
                if doc['id'] == user_id:
                    doctor_id = user_id
                    break
        
        # Last resort - use user_id directly
        if not doctor_id:
            doctor_id = user_id
    
    # Get doctor info
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        # Try to get from config
        for d in config.doctors:
            if d['id'] == doctor_id:
                doctor = type('Doctor', (), d)()
                break
    
    # Get doctor's appointments from database using the correct doctor_id
    doctor_appointments_db = Appointment.query.filter_by(doctor_id=doctor_id).all()
    
    # Convert database appointments to list of dicts
    appointments_list = []
    pending_count = 0
    approved_count = 0
    completed_count = 0
    
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    today_count = 0
    
    for appt in doctor_appointments_db:
        patient = User.query.get(appt.patient_id)
        appointments_list.append({
            'id': appt.id,
            'patient_id': appt.patient_id,
            'patient_name': appt.patient_name or (patient.name if patient else 'Unknown'),
            'doctor_id': appt.doctor_id,
            'doctor_name': appt.doctor_name,
            'specialization': appt.specialization,
            'date': appt.date,
            'time': appt.time,
            'symptoms': appt.symptoms,
            'status': appt.status
        })
        # Correctly count by status
        if appt.status == 'pending':
            pending_count += 1
        elif appt.status in ['Approved', 'approved']:
            approved_count += 1
        elif appt.status in ['Completed', 'completed']:
            completed_count += 1
        if appt.date == today:
            today_count += 1
    
    # Also check in-memory appointments from config (for backward compatibility)
    for appt in config.appointments:
        if appt.get('doctor_id') == doctor_id:
            # Check if this appointment is already in the list
            appt_id = appt.get('id')
            if not any(a.get('id') == appt_id for a in appointments_list):
                patient_id = appt.get('patient_id')
                patient = User.query.get(patient_id) if patient_id else None
                appointments_list.append({
                    'id': appt.get('id'),
                    'patient_id': patient_id,
                    'patient_name': appt.get('patient_name') or (patient.name if patient else 'Unknown'),
                    'doctor_id': appt.get('doctor_id'),
                    'doctor_name': appt.get('doctor_name', ''),
                    'specialization': appt.get('specialization', ''),
                    'date': appt.get('date', ''),
                    'time': appt.get('time', ''),
                    'symptoms': appt.get('symptoms', ''),
                    'status': appt.get('status', 'pending')
                })
                
                status = appt.get('status', 'pending')
                if status == 'pending':
                    pending_count += 1
                elif status in ['Approved', 'approved']:
                    approved_count += 1
                elif status in ['Completed', 'completed']:
                    completed_count += 1
                
                if appt.get('date') == today:
                    today_count += 1
    
    # Get all patients from database
    all_patients = User.query.filter_by(role='patient').all()
    total_patients = len(all_patients)
    
    # Get doctor info if not already found
    if not doctor:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            # Try to get from config
            for d in config.doctors:
                if d['id'] == doctor_id:
                    doctor = type('Doctor', (), d)()
                    break
    
    current_user = session.get('name', 'Doctor')
    
    # Get recent appointments (last 5)
    recent_appointments = sorted(appointments_list, key=lambda x: x.get('id', 0), reverse=True)[:5]
    
    # Calculate total appointments
    total_appointments = len(appointments_list)
    
    return render_template('doctor/dashboard.html', 
                           appointments=appointments_list,
                           recent_appointments=recent_appointments,
                           current_user=current_user,
                           pending_count=pending_count,
                           approved_count=approved_count,
                           completed_count=completed_count,
                           today_appointments=today_count,
                           total_patients=total_patients,
                           total_appointments=total_appointments,
                           doctor=doctor)


# Also support /doctor_dashboard route (without slash)
@app.route('/doctor_dashboard')
def doctor_dashboard_alt():
    return doctor_dashboard()

@app.route('/complete_appointment/<int:id>')
def complete_appointment(id):
    appointment = Appointment.query.get(id)

    if appointment:
        appointment.status = "Completed"
        db.session.commit()
    return redirect(url_for('doctor_dashboard_alt'))


# ==================== DOCTOR PRESCRIPTIONS ROUTE ====================
@app.route('/doctor/prescriptions')
def doctor_prescriptions():
    if not session.get('user_id') or session.get('role') != 'doctor':
        flash('Please login as a doctor', 'warning')
        return redirect(url_for('doctor_login'))
    
    # Get doctor's appointments for patient selection using helper function
    doctor_id = get_doctor_id_from_session()
    doctor_appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
    
    # Get patients
    patients = []
    for appt in doctor_appointments:
        if appt.patient_id not in [p['id'] for p in patients]:
            patient = User.query.get(appt.patient_id)
            if patient:
                patients.append({
                    'id': patient.id,
                    'name': patient.name
                })
    
    current_user = session.get('name', 'Doctor')
    
    # Sample prescriptions data (in real app, this would come from database)
    prescriptions = []
    
    return render_template('doctor/prescriptions.html', 
                           patients=patients,
                           prescriptions=prescriptions,
                           current_user=current_user)


# ==================== DOCTOR ADD PRESCRIPTION ROUTE ====================
@app.route('/doctor/add_prescription', methods=['POST'])
def doctor_add_prescription():
    if not session.get('user_id') or session.get('role') != 'doctor':
        flash('Please login as a doctor', 'warning')
        return redirect(url_for('doctor_login'))
    
    patient_id = request.form.get('patient_id')
    medicine = request.form.get('medicine')
    dosage = request.form.get('dosage')
    days = request.form.get('days')
    notes = request.form.get('notes')
    
    # In a real app, save to database
    flash('Prescription added successfully!', 'success')
    
    return redirect(url_for('doctor_prescriptions'))


# ==================== DOCTOR MEDICAL RECORDS ROUTE ====================
@app.route('/doctor/medical_records')
def doctor_medical_records():
    if not session.get('user_id') or session.get('role') != 'doctor':
        flash('Please login as a doctor', 'warning')
        return redirect(url_for('doctor_login'))
    
    try:
        # Get doctor's appointments for patient selection using helper function
        doctor_id = get_doctor_id_from_session()
        doctor_appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
        
        # Get unique patients from appointments
        patients = []
        for appt in doctor_appointments:
            if appt.patient_id not in [p['id'] for p in patients]:
                patient = User.query.get(appt.patient_id)
                if patient:
                    patients.append({
                        'id': patient.id,
                        'name': patient.name
                    })
        
        # Get medical records from database for this doctor
        db_medical_records = MedicalRecord.query.filter_by(doctor_id=doctor_id).all()
        
        # Convert database records to list of dicts for template
        medical_records = []
        for record in db_medical_records:
            patient = User.query.get(record.patient_id)
            appointment = Appointment.query.get(record.appointment_id) if record.appointment_id else None
            
            medical_records.append({
                'id': record.id,
                'patient_id': record.patient_id,
                'patient_name': patient.name if patient else 'Unknown',
                'date': appointment.date if appointment else (record.created_at.strftime('%Y-%m-%d') if record.created_at else 'N/A'),
                'diagnosis': record.diagnosis or 'N/A',
                'prescriptions': record.prescription or 'No prescriptions',
                'notes': record.notes or '-'
            })
        
        current_user = session.get('name', 'Doctor')
        
        return render_template('doctor/medical_records.html', 
                               patients=patients,
                               medical_records=medical_records,
                               current_user=current_user)
    except Exception as e:
        # Log the error and return a valid response with empty records
        print(f"Error in doctor_medical_records: {e}")
        current_user = session.get('name', 'Doctor')
        return render_template('doctor/medical_records.html', 
                               patients=[],
                               medical_records=[],
                               current_user=current_user)


# ==================== DOCTOR CONSULTATION ROUTE ====================
@app.route('/doctor/consultation')
def doctor_consultation():
    if not session.get('user_id') or session.get('role') != 'doctor':
        flash('Please login as a doctor', 'warning')
        return redirect(url_for('doctor_login'))
    
    # Get the correct doctor_id using the helper function
    doctor_id = get_doctor_id_from_session()
    
    # Get doctor's approved appointments from database
    doctor_appointments_db = Appointment.query.filter_by(doctor_id=doctor_id, status='Approved').all()

    # Get unique patients from database appointments
    patients = []
    seen_patient_ids = set()

    for appt in doctor_appointments_db:
        if appt.patient_id not in seen_patient_ids:
            seen_patient_ids.add(appt.patient_id)
            patient = User.query.get(appt.patient_id)
            if patient:
                patients.append({
                    'id': patient.id,
                    'name': patient.name
                })

    # Also check in-memory appointments from config (for backward compatibility)
    for appt in config.appointments:
        if appt.get('doctor_id') == doctor_id and appt.get('status') == 'Approved':
            patient_id = appt.get('patient_id')
            if patient_id and patient_id not in seen_patient_ids:
                seen_patient_ids.add(patient_id)
                # Try to find patient in database
                patient = User.query.get(patient_id)
                if patient:
                    patients.append({
                        'id': patient.id,
                        'name': patient.name
                    })
                else:
                    # Fallback to patient_name from in-memory
                    patient_name = appt.get('patient_name')
                    if patient_name:
                        patients.append({
                            'id': patient_id,
                            'name': patient_name
                        })

    current_user = session.get('name', 'Doctor')

    return render_template('doctor/consultation.html',
                          patients=patients,
                          current_user=current_user)


# ==================== DOCTOR CONSULTATION WITH APPOINTMENT ID ROUTE ====================
@app.route('/doctor/consultation/<int:appointment_id>')
def doctor_consultation_with_id(appointment_id):
    if not session.get('user_id') or session.get('role') != 'doctor':
        flash('Please login as a doctor', 'warning')
        return redirect(url_for('doctor_login'))
    
    # Get the appointment
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        flash('Appointment not found', 'danger')
        return redirect(url_for('doctor_dashboard'))
    
    # Get the patient from the appointment
    patient = User.query.get(appointment.patient_id)
    selected_patient_id = appointment.patient_id
    
    # Get ALL patients from the database for the dropdown
    all_patients = User.query.filter_by(role='patient').all()
    
    # Convert to list of dicts
    patients = []
    for p in all_patients:
        patients.append({
            'id': p.id,
            'name': p.name
        })
    
    # Also add the current patient if not in the list
    if patient and patient.id not in [p['id'] for p in patients]:
        patients.append({
            'id': patient.id,
            'name': patient.name
        })
    
    current_user = session.get('name', 'Doctor')
    
    return render_template('doctor/consultation.html', 
                          patients=patients,
                          selected_patient_id=selected_patient_id,  
                          appointment=appointment,
                          current_user=current_user)


# ==================== DOCTOR SAVE CONSULTATION ROUTE ====================
@app.route('/doctor/save_consultation', methods=['POST'])
def doctor_save_consultation():
    if not session.get('user_id') or session.get('role') != 'doctor':
        flash('Please login as a doctor', 'warning')
        return redirect(url_for('doctor_login'))
    
    patient_id = request.form.get('patient_id')
    appointment_id = request.form.get('appointment_id')
    symptoms = request.form.get('symptoms')
    diagnosis = request.form.get('diagnosis')
    prescription = request.form.get('prescription')
    notes = request.form.get('notes')

    # Get the correct doctor_id using the helper function
    doctor_id = get_doctor_id_from_session()

    # Get the appointment - either from the hidden field or by finding one
    appointment = None
    if appointment_id:
        appointment = Appointment.query.get(appointment_id)
    else:
        # Try to find an appointment for this patient with this doctor
        appointment = Appointment.query.filter_by(doctor_id=doctor_id, patient_id=patient_id).first()

    # Update appointment status to Completed if appointment exists
    if appointment:
        appointment.status = 'Completed'
        db.session.commit()

    # Save consultation to MedicalRecord table
    new_medical_record = MedicalRecord(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_id=appointment.id if appointment else None,
        diagnosis=diagnosis,
        prescription=prescription,
        notes=notes
    )
    db.session.add(new_medical_record)
    db.session.commit()

    flash('Consultation saved successfully!', 'success')

    return redirect(url_for('doctor_appointments_list'))


# ==================== DOCTOR PATIENTS ROUTE ====================
@app.route('/doctor/patients')
def doctor_patients():
    if not session.get('user_id') or session.get('role') != 'doctor':
        flash('Please login as a doctor', 'warning')
        return redirect(url_for('doctor_login'))
    
    # Get all patients from database
    patients_list = User.query.filter_by(role='patient').all()
    
    return render_template('doctor/patients.html', patients=patients_list)


# ==================== DOCTOR PATIENT DETAIL ROUTE ====================
@app.route('/doctor/patient/<int:patient_id>')
def doctor_patient_detail(patient_id):
    if not session.get('user_id') or session.get('role') != 'doctor':
        flash('Please login as a doctor', 'warning')
        return redirect(url_for('doctor_login'))
    
    # Get the patient from database
    patient = User.query.get(patient_id)
    
    if not patient:
        flash('Patient not found', 'danger')
        return redirect(url_for('doctor_patients'))
    
    # Get ALL appointments for this patient (not just with current doctor)
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()
    
    # Get ALL medical records for this patient
    medical_records = MedicalRecord.query.filter_by(patient_id=patient_id).all()
    
    # Get list of doctors for the add medical record form
    doctors = Doctor.query.all()
    
    current_user = session.get('name', 'Doctor')
    
    return render_template('doctor/patient_detail.html', 
                          patient=patient,
                          appointments=appointments,
                          medical_records=medical_records,
                          doctors=doctors,
                          current_user=current_user)


# ==================== DOCTOR ADD MEDICAL RECORD ROUTE ====================
@app.route('/doctor/add_medical_record', methods=['POST'])
def doctor_add_medical_record():
    if not session.get('user_id') or session.get('role') != 'doctor':
        flash('Please login as a doctor', 'warning')
        return redirect(url_for('doctor_login'))
    
    patient_id = request.form.get('patient_id')
    diagnosis = request.form.get('diagnosis', '')
    prescription = request.form.get('prescription', '')
    notes = request.form.get('notes', '')
    appointment_id = request.form.get('appointment_id')
    
    doctor_id = session.get('user_id')
    
    # Validate patient exists
    patient = User.query.get(patient_id)
    if not patient:
        flash('Patient not found', 'danger')
        return redirect(url_for('doctor_patients'))
    
    # Create new medical record
    new_record = MedicalRecord(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_id=appointment_id if appointment_id else None,
        diagnosis=diagnosis,
        prescription=prescription,
        notes=notes
    )
    db.session.add(new_record)
    db.session.commit()
    
    flash('Medical record added successfully!', 'success')
    
    return redirect(url_for('doctor_patient_detail', patient_id=patient_id))

# ==================== DOCTOR APPOINTMENTS LIST ROUTE ====================
@app.route('/doctor/appointments_list')
def doctor_appointments_list():
    if not session.get('user_id') or session.get('role') != 'doctor':
        flash('Please login as a doctor', 'warning')
        return redirect(url_for('doctor_login'))
    
    # Use the helper function to get the correct doctor_id from session
    # This ensures we get the actual doctor_id from the Doctor table
    doctor_id = get_doctor_id_from_session()

    # Get doctor's appointments from database (sorted by newest first)
    # This correctly filters by doctor_id regardless of status
    doctor_appointments_db = Appointment.query.order_by(Appointment.id.desc()).all()
    appointments_list = []
    
    # Convert database appointments to list of dicts
    for appt in doctor_appointments_db:
        patient = User.query.get(appt.patient_id)
        appointments_list.append({
            'id': appt.id,
            'patient_id': appt.patient_id,
            'patient_name': appt.patient_name or (patient.name if patient else 'Unknown'),
            'doctor_id': appt.doctor_id,
            'doctor_name': appt.doctor_name,
            'specialization': appt.specialization,
            'date': appt.date,
            'time': appt.time,
            'symptoms': appt.symptoms,
            'status': appt.status
        })
    
    # Check in-memory appointments (config) for backward compatibility
    for appt in config.appointments:
        if appt.get('doctor_id') == doctor_id:
            appt_id = appt.get('id')
            if not any(a.get('id') == appt_id for a in appointments_list):
                patient_id = appt.get('patient_id')
                patient = User.query.get(patient_id) if patient_id else None
                appointments_list.append({
                    'id': appt.get('id'),
                    'patient_id': patient_id,
                    'patient_name': appt.get('patient_name') or (patient.name if patient else 'Unknown'),
                    'doctor_id': appt.get('doctor_id'),
                    'doctor_name': appt.get('doctor_name', ''),
                    'specialization': appt.get('specialization', ''),
                    'date': appt.get('date', ''),
                    'time': appt.get('time', ''),
                    'symptoms': appt.get('symptoms', ''),
                    'status': appt.get('status', 'pending')
                })
    
    return render_template(
        'doctor/appointments.html',
        appointments=sorted(appointments_list, key=lambda x: x.get('id', 0), reverse=True))
    
    
# ==================== DOCTOR APPOINTMENT UPDATE ROUTES ====================
@app.route('/doctor/appointment/<int:id>/update', methods=['POST'])
def doctor_update_appointment(id):
    """Update appointment status - Accept, Reject, or Complete"""
    if not session.get('user_id') or session.get('role') != 'doctor':
        flash('Please login as a doctor', 'warning')
        return redirect(url_for('doctor_login'))
    
    # Get the correct doctor_id using the helper function
    doctor_id = get_doctor_id_from_session()
    action = request.form.get('action')
    
    # Find the appointment
    appointment = Appointment.query.get(id)
    
    if not appointment:
        flash('Appointment not found', 'danger')
        return redirect(url_for('doctor_dashboard'))
    
    # Check if doctor owns this appointment
    if appointment.doctor_id != doctor_id:
        flash('You can only update your own appointments', 'danger')
        return redirect(url_for('doctor_dashboard'))
    
    # Update status based on action
    if action == 'accept':
        appointment.status = 'Approved'
        flash('Appointment accepted successfully!', 'success')
    elif action == 'reject':
        appointment.status = 'Cancelled'
        flash('Appointment rejected', 'info')
    elif action == 'complete':
        appointment.status = 'Completed'
        flash('Appointment marked as completed', 'success')
    else:
        flash('Invalid action', 'danger')
    
    db.session.commit()
    return redirect(url_for('doctor_dashboard'))


@app.route('/admin/approve_appointment/<int:appointment_id>')
def approve_appointment(appointment_id):
    if not session.get('user_id') or session.get('role') != 'admin':
        flash('Please login as admin', 'warning')
        return redirect(url_for('admin_login'))
    
    # Update in database
    appt = Appointment.query.get(appointment_id)
    if appt:
        appt.status = 'approved'
        db.session.commit()
        
        # Get patient info from User model - try multiple ways to find patient
        patient = None
        patient_email = None
        
        # First try: Query by patient_id
        if appt.patient_id:
            patient = User.query.get(appt.patient_id)
        
        # If not found by ID, try to find by patient_name (fallback)
        if not patient and appt.patient_name:
            patient = User.query.filter_by(name=appt.patient_name).first()
        
        # Get patient email if patient found
        if patient:
            patient_email = getattr(patient, 'email', None)
            # Also try to get email from config users as fallback
            if not patient_email:
                for u in config.users:
                    if u.get('name') == patient.name:
                        patient_email = u.get('email')
                        break
        
        doctor = Doctor.query.get(appt.doctor_id)
        
        # Send email to patient if email found
        if patient_email:
            try:
                subject = "Appointment Status Update"
                body = f"""Hello {patient.name},

Your appointment with {doctor.name if doctor else appt.doctor_name} on {appt.date} at {appt.time} has been Approved.

Thank you,
Hospital Management System"""
                
                msg = Message(subject, recipients=[patient_email], body=body)
                mail.send(msg)
                flash(f'Appointment approved! Email sent to {patient_email}', 'success')
            except Exception as e:
                flash(f'Appointment approved but email failed: {str(e)}', 'warning')
        else:
            flash('Appointment approved successfully (patient email not found)', 'success')
    else:
        flash('Appointment not found', 'danger')
    
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/reject_appointment/<int:appointment_id>')
def reject_appointment(appointment_id):
    if not session.get('user_id') or session.get('role') != 'admin':
        flash('Please login as admin', 'warning')
        return redirect(url_for('admin_login'))
    
    # Update in database
    appt = Appointment.query.get(appointment_id)
    if appt:
        appt.status = 'rejected'
        db.session.commit()
        
        # Get patient info from User model - try multiple ways to find patient
        patient = None
        patient_email = None
        
        # First try: Query by patient_id
        if appt.patient_id:
            patient = User.query.get(appt.patient_id)
        
        # If not found by ID, try to find by patient_name (fallback)
        if not patient and appt.patient_name:
            patient = User.query.filter_by(name=appt.patient_name).first()
        
        # Get patient email if patient found
        if patient:
            patient_email = getattr(patient, 'email', None)
            # Also try to get email from config users as fallback
            if not patient_email:
                for u in config.users:
                    if u.get('name') == patient.name:
                        patient_email = u.get('email')
                        break
        
        doctor = Doctor.query.get(appt.doctor_id)
        
        # Send email to patient if email found
        if patient_email:
            try:
                subject = "Appointment Status Update"
                body = f"""Hello {patient.name},

Your appointment with {doctor.name if doctor else appt.doctor_name} on {appt.date} at {appt.time} has been Rejected.

Thank you,
Hospital Management System"""
                
                msg = Message(subject, recipients=[patient_email], body=body)
                mail.send(msg)
                flash(f'Appointment rejected! Email sent to {patient_email}', 'success')
            except Exception as e:
                flash(f'Appointment rejected but email failed: {str(e)}', 'warning')
        else:
            flash('Appointment rejected successfully (patient email not found)', 'success')
    else:
        flash('Appointment not found', 'danger')
    
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/delete_appointment/<int:appointment_id>')
def delete_appointment(appointment_id):
    if not session.get('user_id') or session.get('role') != 'admin':
        flash('Please login as admin', 'warning')
        return redirect(url_for('admin_login'))
    
    # Delete from database
    appt = Appointment.query.get(appointment_id)
    if appt:
        db.session.delete(appt)
        db.session.commit()
        flash('Appointment deleted successfully', 'success')
    else:
        flash('Appointment not found', 'danger')
    
    return redirect(url_for('admin_dashboard'))


# ==================== DELETE MEDICAL RECORD ROUTE ====================
@app.route('/admin/delete_medical_record/<int:record_id>')
def delete_medical_record(record_id):
    if not session.get('user_id') or session.get('role') != 'admin':
        flash('Please login as admin', 'warning')
        return redirect(url_for('admin_login'))
    
    # Delete medical record from database
    record = MedicalRecord.query.get(record_id)
    if record:
        db.session.delete(record)
        db.session.commit()
        flash('Patient history record deleted successfully', 'success')
    else:
        flash('Record not found', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/patient/book_appointment', methods=['POST'])
def book_appointment():

    if not session.get('user_id'):
        flash("Please login first")
        return redirect(url_for('patient_login'))

    doctor_id = int(request.form.get('doctor_id'))
    appointment_date = request.form.get('appointment_date')
    appointment_time = request.form.get('appointment_time')
    symptoms = request.form.get('symptoms', '')

    patient_id = session.get('user_id')
    patient_name = session.get('name')

    # Get doctor from database
    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        flash("Doctor not found")
        return redirect(url_for('patient_dashboard'))

    # Create appointment
    new_appointment = Appointment(
        patient_id=patient_id,
        patient_name=patient_name,
        doctor_id=doctor.id,
        doctor_name=doctor.name,
        specialization=doctor.specialization,
        date=appointment_date,
        time=appointment_time,
        symptoms=symptoms,
        status='pending'
    )

    db.session.add(new_appointment)
    db.session.commit()

    flash('Appointment booked successfully!', 'success')

    return redirect(url_for('patient_dashboard'))


# ==================== PATIENT MEDICAL RECORDS ROUTE ====================
@app.route('/patient/medical_records')
def patient_medical_records():
    """View patient's medical records"""
    # Check if user is logged in
    if not session.get('user_id'):
        flash('Please login to view your medical records', 'warning')
        return redirect(url_for('login_page'))
    
    # Get the logged-in patient's ID
    patient_id = session.get('user_id')
    
    # Get all medical records for this patient from database
    db_medical_records = MedicalRecord.query.filter_by(patient_id=patient_id).all()
    
    # Convert database records to list of dicts for template
    medical_records = []
    for record in db_medical_records:
        doctor = Doctor.query.get(record.doctor_id)
        appointment = Appointment.query.get(record.appointment_id) if record.appointment_id else None
        
        medical_records.append({
            'id': record.id,
            'doctor_name': doctor.name if doctor else 'Unknown Doctor',
            'specialization': doctor.specialization if doctor else 'General',
            'date': appointment.date if appointment else (record.created_at.strftime('%Y-%m-%d') if record.created_at else 'N/A'),
            'diagnosis': record.diagnosis or 'No diagnosis',
            'prescription': record.prescription or 'No prescription',
            'notes': record.notes or '-'
        })
    
    return render_template('patient/medical_records.html', medical_records=medical_records)


# ==================== API ROUTES ====================
@app.route('/api/my_appointments')
def api_my_appointments():
    """API to get appointments for the logged-in patient"""
    patient_id = session.get('user_id')
    
    if not patient_id:
        return jsonify([])
    
    # Get appointments for this patient from database
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()
    
    appointments_list = []
    for appt in appointments:
        doctor = Doctor.query.get(appt.doctor_id)
        appointments_list.append({
            'id': appt.id,
            'patient_id': appt.patient_id,
            'doctor_id': appt.doctor_id,
            'doctor_name': appt.doctor_name,
            'specialization': appt.specialization,
            'date': appt.date,
            'time': appt.time,
            'symptoms': appt.symptoms,
            'status': appt.status
        })
    
    return jsonify(appointments_list)


# ==================== REGISTER API ROUTE ====================
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Invalid registration data'}), 400
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    age = data.get('age')
    gender = data.get('gender')
    
    if not name or not email or not password:
        return jsonify({'message': 'Name, email and password are required'}), 400
    
    # Check in config users first
    for user in config.users:
        if user.get('email') == email:
            return jsonify({'message': 'Email already registered'}), 400
    
    # Also check in database
    existing_db_user = User.query.filter_by(email=email).first()
    if existing_db_user:
        return jsonify({'message': 'Email already registered'}), 400
    
    # Save to database
    new_user = User(
        name=name,
        email=email,
        password=password,
        age=age,
        gender=gender,
        role='patient'
    )
    db.session.add(new_user)
    db.session.commit()
    
    # Also save to config for backward compatibility
    new_user_config = {
        'id': config.user_id_counter,
        'name': name,
        'email': email,
        'password': password,
        'age': age,
        'gender': gender,
        'role': 'patient'
    }
    config.user_id_counter += 1
    config.users.append(new_user_config)
    
    return jsonify({'message': 'Registration successful'}), 200


# ==================== LOGOUT ROUTE ====================
@app.route('/logout')
def logout():
    """Logout user and redirect to home"""
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))


# ==================== LOGIN API ROUTE ====================
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Invalid login data'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400
    
    user = None
    
    # First check in config users
    for u in config.users:
        if u.get('email') == email and u.get('password') == password:
            user = u
            break
    
    # If not found in config, check in database
    if not user:
        db_user = User.query.filter_by(email=email, password=password).first()
        if db_user:
            user = {
                'id': db_user.id,
                'name': db_user.name,
                'email': db_user.email,
                'password': db_user.password,
                'age': db_user.age,
                'gender': db_user.gender,
                'role': db_user.role
            }
    
    if user:
        session['user_id'] = user.get('id')
        session['email'] = user.get('email')
        session['name'] = user.get('name')
        session['role'] = user.get('role')
        
        redirect_url = '/patient/dashboard'
        if user.get('role') == 'admin':
            redirect_url = '/admin/dashboard'
        elif user.get('role') == 'doctor':
            redirect_url = '/doctor/dashboard'
        
        return jsonify({
            'message': 'Login successful',
            'redirect': redirect_url
        }), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401


# ==================== MAIN ====================
if __name__ == "__main__":

    print("=" * 50)
    print("CareConnect - Patient Login System")
    print("=" * 50)
    print("Database: SQLite (database.db)")
    print("")

    print("HTML Pages:")
    print(" http://127.0.0.1:5000/ - Home Page")
    print(" http://127.0.0.1:5000/login-page - Login Page")
    print(" http://127.0.0.1:5000/register-page - Register Page")
    print("")

    print("API Endpoints:")
    print(" GET /test-db - Test database connection")
    print(" POST /register - Register new user")
    print(" POST /login - User login")
    print("=" * 50)

    # Create database tables and seed data - ALL INSIDE APP CONTEXT
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Seed doctors from config if they don't exist
        for doc in config.doctors:
            existing = Doctor.query.get(doc['id'])
            if not existing:
                new_doctor = Doctor(
                    id=doc['id'],
                    name=doc['name'],
                    specialization=doc['specialization'],
                    experience=doc.get('experience', '')
                )
                db.session.add(new_doctor)
        
        # Seed admin user if not exists
        admin = User.query.filter_by(email='sanjayadmin@gmail.com').first()
        if not admin:
            admin_user = User(
                name='Admin',
                email='sanjayadmin@gmail.com',
                password='admin123',
                role='admin'
            )
            db.session.add(admin_user)
        
        db.session.commit()
        print("✓ Seed data added successfully!")
    
    # Run the app (only once, after all initialization is complete)
    app.run(debug=True, host='127.0.0.1', port=5000)

