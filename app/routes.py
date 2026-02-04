"""
All application routes in one file.

Why one file?
- Small app = one file is fine and easier to navigate
- No need to hunt across multiple files
- Split when this grows beyond ~300 lines
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models import User, Role, PatientDetails, DoctorPatient
from app.auth import login_required, role_required, get_current_user_id, get_current_user_role

main_bp = Blueprint('main', __name__)


# =============================================================================
# PUBLIC ROUTES
# =============================================================================

@main_bp.route('/')
def index():
    """Home page - redirect to dashboard if logged in, else to login."""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page and form handler.
    
    GET: Show login form
    POST: Validate credentials and create session
    """
    # Already logged in? Go to dashboard
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Valid credentials - create session
            session['user_id'] = user.id
            session['user_role'] = user.role.name
            session['user_name'] = user.full_name
            flash(f'Welcome, {user.full_name}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')


@main_bp.route('/logout')
def logout():
    """Clear session and redirect to login."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))


# =============================================================================
# DASHBOARD - Routes user to appropriate dashboard based on role
# =============================================================================

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Main dashboard router.
    Redirects to role-specific dashboard based on user's role.
    """
    role = get_current_user_role()
    
    if role == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    elif role == 'doctor':
        return redirect(url_for('main.doctor_dashboard'))
    elif role == 'patient':
        return redirect(url_for('main.patient_dashboard'))
    else:
        flash('Unknown role. Please contact administrator.', 'error')
        return redirect(url_for('main.logout'))


# =============================================================================
# ADMIN ROUTES
# =============================================================================

@main_bp.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    """
    Admin dashboard: view all users and all patients.
    """
    # Get all users grouped by role
    all_users = User.query.join(Role).order_by(Role.name, User.full_name).all()
    
    # Get all patient details
    all_patients = PatientDetails.query.join(User).order_by(User.full_name).all()
    
    return render_template('admin_dashboard.html', 
                         users=all_users, 
                         patients=all_patients)


# =============================================================================
# DOCTOR ROUTES
# =============================================================================

@main_bp.route('/doctor/dashboard')
@login_required
@role_required('doctor')
def doctor_dashboard():
    """
    Doctor dashboard: view only assigned patients.
    """
    doctor_id = get_current_user_id()
    
    # Get patients assigned to this doctor
    # Using join to get patient details in one query
    assigned = (
        db.session.query(User, PatientDetails)
        .join(DoctorPatient, DoctorPatient.patient_id == User.id)
        .outerjoin(PatientDetails, PatientDetails.user_id == User.id)
        .filter(DoctorPatient.doctor_id == doctor_id)
        .order_by(User.full_name)
        .all()
    )
    
    return render_template('doctor_dashboard.html', patients=assigned)


@main_bp.route('/doctor/patient/<int:patient_id>')
@login_required
@role_required('doctor')
def doctor_view_patient(patient_id):
    """
    Doctor views a specific patient's details.
    Only allowed if patient is assigned to this doctor.
    """
    doctor_id = get_current_user_id()
    
    # Check if this patient is assigned to this doctor
    assignment = DoctorPatient.query.filter_by(
        doctor_id=doctor_id, 
        patient_id=patient_id
    ).first()
    
    if not assignment:
        flash('You are not authorized to view this patient.', 'error')
        return redirect(url_for('main.doctor_dashboard'))
    
    # Get patient and their details
    patient = User.query.get(patient_id)
    details = PatientDetails.query.filter_by(user_id=patient_id).first()
    
    return render_template('patient_view.html', patient=patient, details=details)


@main_bp.route('/doctor/patient/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('doctor')
def doctor_edit_patient(patient_id):
    """
    Doctor edits a patient's medical notes.
    Only allowed if patient is assigned to this doctor.
    """
    doctor_id = get_current_user_id()
    
    # Check authorization
    assignment = DoctorPatient.query.filter_by(
        doctor_id=doctor_id, 
        patient_id=patient_id
    ).first()
    
    if not assignment:
        flash('You are not authorized to edit this patient.', 'error')
        return redirect(url_for('main.doctor_dashboard'))
    
    patient = User.query.get(patient_id)
    details = PatientDetails.query.filter_by(user_id=patient_id).first()
    
    # Create details record if it doesn't exist
    if not details:
        details = PatientDetails(user_id=patient_id)
        db.session.add(details)
    
    if request.method == 'POST':
        details.medical_notes = request.form.get('medical_notes', '')
        details.phone = request.form.get('phone', '')
        db.session.commit()
        flash('Patient details updated.', 'success')
        return redirect(url_for('main.doctor_view_patient', patient_id=patient_id))
    
    return render_template('patient_edit.html', patient=patient, details=details)


# =============================================================================
# PATIENT ROUTES
# =============================================================================

@main_bp.route('/patient/dashboard')
@login_required
@role_required('patient')
def patient_dashboard():
    """
    Patient dashboard: view only their own details.
    """
    user_id = get_current_user_id()
    
    # Get current user and their patient details
    patient = User.query.get(user_id)
    details = PatientDetails.query.filter_by(user_id=user_id).first()
    
    # Get assigned doctors
    assigned_doctors = (
        User.query
        .join(DoctorPatient, DoctorPatient.doctor_id == User.id)
        .filter(DoctorPatient.patient_id == user_id)
        .all()
    )
    
    return render_template('patient_dashboard.html', 
                         patient=patient, 
                         details=details,
                         doctors=assigned_doctors)

