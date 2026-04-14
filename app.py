import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import cv_generator
import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eme4you-cv-bot-2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CV_FOLDER'] = 'generated_cvs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Create necessary folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CV_FOLDER'], exist_ok=True)

# Initialize database
db.init_db()

@app.route('/')
def index():
    """Home page with CV creation form"""
    return render_template('index.html')

@app.route('/create_cv', methods=['POST'])
def create_cv():
    """Generate CV from form data"""
    try:
        # 1. Personal Information
        personal_info = {
            'full_name': request.form.get('full_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'linkedin': request.form.get('linkedin', ''),
            'portfolio': request.form.get('portfolio', '')
        }
        
        # 2. Professional Summary
        professional_summary = request.form.get('professional_summary')
        
        # 3. Work Experience
        job_titles = request.form.getlist('job_title[]')
        companies = request.form.getlist('company[]')
        start_dates = request.form.getlist('start_date[]')
        end_dates = request.form.getlist('end_date[]')
        responsibilities = request.form.getlist('responsibilities[]')
        
        work_experience = []
        for i in range(len(job_titles)):
            if job_titles[i] and companies[i]:
                work_experience.append({
                    'title': job_titles[i],
                    'company': companies[i],
                    'start_date': start_dates[i] if i < len(start_dates) else '',
                    'end_date': end_dates[i] if i < len(end_dates) else '',
                    'responsibilities': responsibilities[i] if i < len(responsibilities) else ''
                })
        
        # 4. Education
        degrees = request.form.getlist('degree[]')
        institutions = request.form.getlist('institution[]')
        grad_years = request.form.getlist('grad_year[]')
        
        education = []
        for i in range(len(degrees)):
            if degrees[i] and institutions[i]:
                education.append({
                    'degree': degrees[i],
                    'institution': institutions[i],
                    'grad_year': grad_years[i] if i < len(grad_years) else ''
                })
        
        # 5. Skills
        skills = request.form.get('skills', '').split(',')
        skills = [s.strip() for s in skills if s.strip()]
        
        # 6. Certifications
        cert_names = request.form.getlist('cert_name[]')
        cert_issuers = request.form.getlist('cert_issuer[]')
        cert_years = request.form.getlist('cert_year[]')
        
        certifications = []
        for i in range(len(cert_names)):
            if cert_names[i]:
                certifications.append({
                    'name': cert_names[i],
                    'issuer': cert_issuers[i] if i < len(cert_issuers) else '',
                    'year': cert_years[i] if i < len(cert_years) else ''
                })
        
        # 7. Languages
        languages = request.form.get('languages', '').split(',')
        languages = [l.strip() for l in languages if l.strip()]
        
        # 8. Handle document uploads
        id_file = request.files.get('id_doc')
        proof_file = request.files.get('proof_doc')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], f"{personal_info['full_name'].replace(' ', '_')}_{timestamp}")
        os.makedirs(user_folder, exist_ok=True)
        
        if id_file:
            id_path = os.path.join(user_folder, secure_filename(f"certified_id.pdf"))
            id_file.save(id_path)
        else:
            id_path = None
            
        if proof_file:
            proof_path = os.path.join(user_folder, secure_filename(f"proof_of_residence.pdf"))
            proof_file.save(proof_path)
        else:
            proof_path = None
        
        # 9. Save to database
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (full_name, email, phone, address, professional_summary, skills, languages, 
                             doc_id_path, doc_proof_path, submission_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (personal_info['full_name'], personal_info['email'], personal_info['phone'], 
              personal_info['address'], professional_summary, ','.join(skills), ','.join(languages),
              id_path, proof_path, datetime.now()))
        
        user_id = cursor.lastrowid
        
        # Save work experience
        for exp in work_experience:
            cursor.execute('''
                INSERT INTO work_experience (user_id, job_title, company, start_date, end_date, responsibilities)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, exp['title'], exp['company'], exp['start_date'], exp['end_date'], exp['responsibilities']))
        
        # Save education
        for edu in education:
            cursor.execute('''
                INSERT INTO education (user_id, degree, institution, graduation_year)
                VALUES (?, ?, ?, ?)
            ''', (user_id, edu['degree'], edu['institution'], edu['grad_year']))
        
        # Save certifications
        for cert in certifications:
            cursor.execute('''
                INSERT INTO certifications (user_id, cert_name, issuer, year)
                VALUES (?, ?, ?, ?)
            ''', (user_id, cert['name'], cert['issuer'], cert['year']))
        
        conn.commit()
        conn.close()
        
        # 10. Generate ATS-Compliant CV
        cv_data = {
            'personal_info': personal_info,
            'professional_summary': professional_summary,
            'work_experience': work_experience,
            'education': education,
            'skills': skills,
            'certifications': certifications,
            'languages': languages
        }
        
        cv_filename = f"{personal_info['full_name'].replace(' ', '_')}_{timestamp}.pdf"
        cv_path = os.path.join(app.config['CV_FOLDER'], cv_filename)
        
        cv_generator.generate_ats_cv(cv_data, cv_path)
        
        # Store CV path in database
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET cv_path = ? WHERE id = ?', (cv_path, user_id))
        conn.commit()
        conn.close()
        
        return render_template('success.html', 
                             user_name=personal_info['full_name'],
                             cv_filename=cv_filename,
                             user_id=user_id)
    
    except Exception as e:
        flash(f'Error creating CV: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download_cv/<filename>')
def download_cv(filename):
    """Download generated CV"""
    cv_path = os.path.join(app.config['CV_FOLDER'], filename)
    if os.path.exists(cv_path):
        return send_file(cv_path, as_attachment=True, download_name=filename)
    else:
        flash('CV file not found', 'error')
        return redirect(url_for('index'))

@app.route('/admin')
def admin():
    """Admin view all CV submissions"""
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY submission_date DESC')
    users = cursor.fetchall()
    conn.close()
    return render_template('admin.html', users=users)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)