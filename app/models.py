"""
Database models using SQLAlchemy.

Schema Design:
- User: Base table for all users (admins, doctors, patients)
- Role: Simple enum-like table (admin, doctor, patient)
- DoctorPatient: Many-to-many mapping between doctors and patients

Why one User table instead of separate tables per role?
- Simpler login logic (one table to query)
- Roles are just access levels, not fundamentally different entities
- Easier to extend (e.g., a user could have multiple roles later)
"""
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class Role(db.Model):
    """
    Role table: admin, doctor, patient
    Using a table instead of enum for flexibility and readability in queries.
    """
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model):
    """
    All users in the system: admins, doctors, and patients.
    Role determines what they can see and do.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    
    # Relationship to Role
    role = db.relationship('Role', backref='users')
    
    def set_password(self, password):
        """Hash and store password. Never store plain text passwords."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class PatientDetails(db.Model):
    """
    Extra details for users who are patients.
    Linked 1:1 with User table where role='patient'.
    
    Why separate table?
    - Not all users have patient data (admins, doctors don't)
    - Keeps User table clean and focused on auth
    """
    __tablename__ = 'patient_details'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    medical_notes = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # Relationship to User
    user = db.relationship('User', backref=db.backref('patient_details', uselist=False))
    
    def __repr__(self):
        return f'<PatientDetails for user_id={self.user_id}>'


class DoctorPatient(db.Model):
    """
    Mapping table: which doctors are assigned to which patients.
    A doctor can have many patients.
    A patient can have multiple doctors (e.g., specialist + GP).
    """
    __tablename__ = 'doctor_patient'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Unique constraint: same doctor-patient pair shouldn't exist twice
    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'patient_id', name='unique_doctor_patient'),
    )
    
    # Relationships
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='assigned_patients')
    patient = db.relationship('User', foreign_keys=[patient_id], backref='assigned_doctors')
    
    def __repr__(self):
        return f'<DoctorPatient doctor={self.doctor_id} patient={self.patient_id}>'

