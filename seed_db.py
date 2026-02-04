"""
Database seeding script.

This script initializes the database with tables and demo data.
Run this after the containers are up and MySQL is ready.

Usage:
    python seed_db.py

What it does:
1. Creates all tables (if they don't exist)
2. Inserts roles (admin, doctor, patient)
3. Creates demo users with proper password hashes
4. Creates sample patient data
5. Creates doctor-patient assignments
"""
import sys
import time
from sqlalchemy.exc import OperationalError
from app import create_app, db
from app.models import Role, User, PatientDetails, DoctorPatient


def wait_for_db(app, max_retries=30, delay=2):
    """
    Wait for the database to be ready.
    MySQL container might take a few seconds to initialize.
    """
    print("Waiting for database to be ready...")
    for attempt in range(max_retries):
        try:
            with app.app_context():
                # Try to connect
                db.engine.connect()
                print("Database is ready!")
                return True
        except OperationalError as e:
            print(f"  Attempt {attempt + 1}/{max_retries}: Database not ready yet...")
            time.sleep(delay)
    
    print("ERROR: Could not connect to database after multiple attempts.")
    return False


def seed_database():
    """Create tables and insert demo data."""
    app = create_app()
    
    # Wait for database to be available
    if not wait_for_db(app):
        sys.exit(1)
    
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        
        # Check if data already exists
        if Role.query.first():
            print("Database already seeded. Skipping.")
            return
        
        print("Inserting roles...")
        roles = [
            Role(id=1, name='admin'),
            Role(id=2, name='doctor'),
            Role(id=3, name='patient'),
        ]
        for role in roles:
            db.session.add(role)
        db.session.commit()
        
        print("Creating users...")
        
        # Admin user
        admin = User(
            username='admin',
            full_name='System Administrator',
            email='admin@hospital.com',
            role_id=1
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Doctor users
        dr_smith = User(
            username='dr_smith',
            full_name='Dr. Sarah Smith',
            email='dr.smith@hospital.com',
            role_id=2
        )
        dr_smith.set_password('doctor123')
        db.session.add(dr_smith)
        
        dr_jones = User(
            username='dr_jones',
            full_name='Dr. Michael Jones',
            email='dr.jones@hospital.com',
            role_id=2
        )
        dr_jones.set_password('doctor123')
        db.session.add(dr_jones)
        
        # Patient users
        john = User(
            username='john_doe',
            full_name='John Doe',
            email='john.doe@email.com',
            role_id=3
        )
        john.set_password('patient123')
        db.session.add(john)
        
        jane = User(
            username='jane_wilson',
            full_name='Jane Wilson',
            email='jane.wilson@email.com',
            role_id=3
        )
        jane.set_password('patient123')
        db.session.add(jane)
        
        bob = User(
            username='bob_brown',
            full_name='Bob Brown',
            email='bob.brown@email.com',
            role_id=3
        )
        bob.set_password('patient123')
        db.session.add(bob)
        
        db.session.commit()
        print("Users created.")
        
        # Get user IDs (they were auto-assigned)
        john = User.query.filter_by(username='john_doe').first()
        jane = User.query.filter_by(username='jane_wilson').first()
        bob = User.query.filter_by(username='bob_brown').first()
        dr_smith = User.query.filter_by(username='dr_smith').first()
        dr_jones = User.query.filter_by(username='dr_jones').first()
        
        print("Creating patient details...")
        patient_details = [
            PatientDetails(
                user_id=john.id,
                date_of_birth=None,  # Simplified: not setting dates
                medical_notes='Regular checkup. Blood pressure normal. No concerns.',
                phone='(555) 123-4567'
            ),
            PatientDetails(
                user_id=jane.id,
                date_of_birth=None,
                medical_notes='Mild allergies to pollen. Prescribed antihistamines.',
                phone='(555) 234-5678'
            ),
            PatientDetails(
                user_id=bob.id,
                date_of_birth=None,
                medical_notes='Type 2 diabetes. On metformin. Monitor blood sugar levels.',
                phone='(555) 345-6789'
            ),
        ]
        for pd in patient_details:
            db.session.add(pd)
        db.session.commit()
        
        print("Assigning patients to doctors...")
        assignments = [
            DoctorPatient(doctor_id=dr_smith.id, patient_id=john.id),
            DoctorPatient(doctor_id=dr_smith.id, patient_id=jane.id),
            DoctorPatient(doctor_id=dr_jones.id, patient_id=jane.id),  # Shared patient
            DoctorPatient(doctor_id=dr_jones.id, patient_id=bob.id),
        ]
        for assignment in assignments:
            db.session.add(assignment)
        db.session.commit()
        
        print("\n" + "="*50)
        print("Database seeded successfully!")
        print("="*50)
        print("\nDemo credentials:")
        print("  Admin:   admin / admin123")
        print("  Doctor:  dr_smith / doctor123")
        print("  Doctor:  dr_jones / doctor123")
        print("  Patient: john_doe / patient123")
        print("  Patient: jane_wilson / patient123")
        print("  Patient: bob_brown / patient123")
        print("="*50)


if __name__ == '__main__':
    seed_database()

