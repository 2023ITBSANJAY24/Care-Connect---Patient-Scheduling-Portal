# TODO - Fix Doctor Dashboard to Show Doctor-Specific Appointments

## Task
Fix the doctor dashboard so each doctor only sees their own appointments based on doctor_id from the appointments table.

## Problem Analysis
- Doctor login stores user_id (from config.users) in session
- But appointments use doctor_id (from doctors table/database)
- Mismatch causes all doctors to see same/incorrect data

## Fix Plan

### Step 1: Modify doctor_login_api in app.py
- After successful login, find the doctor's actual ID from Doctor table
- Store doctor_id in session alongside user_id

### Step 2: Modify doctor_dashboard in app.py
- Use session.get('doctor_id') directly if available
- Keep existing fallback logic for backward compatibility

## Implementation Steps
- [x] 1. Update doctor_login_api to store doctor_id in session
- [x] 2. Update doctor_dashboard to use doctor_id from session
- [x] 3. Test the fix

