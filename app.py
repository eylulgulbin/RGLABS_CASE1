"""
Hackathon Platform - Flask Application
A comprehensive platform for managing hackathon events
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from mysql.connector import Error
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# MySQL database configuration
app.config['DB_HOST'] = 'localhost'
app.config['DB_USER'] = 'root'
app.config['DB_PASSWORD'] = 'egy123456'
app.config['DB_NAME'] = 'hackathon2'

# Database helper functions
def get_db():
    """Get database connection"""
    try:
        db = mysql.connector.connect(
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME']
        )
        return db
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise

def init_db():
    """Initialize the database with schema"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(64) NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL DEFAULT 'participant',
            bio TEXT,
            github_username VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Hackathons table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hackathons (
            id INT AUTO_INCREMENT PRIMARY KEY,
            organizer_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            registration_deadline TIMESTAMP NOT NULL,
            max_team_size INT DEFAULT 4,
            min_team_size INT DEFAULT 1,
            status VARCHAR(50) DEFAULT 'draft',
            is_online BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organizer_id) REFERENCES users(id)
        )
    ''')
    
    # Teams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INT AUTO_INCREMENT PRIMARY KEY,
            hackathon_id INT NOT NULL,
            team_name VARCHAR(255) NOT NULL,
            team_leader_id INT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hackathon_id) REFERENCES hackathons(id),
            FOREIGN KEY (team_leader_id) REFERENCES users(id),
            UNIQUE(hackathon_id, team_name)
        )
    ''')
    
    # Team members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            id INT AUTO_INCREMENT PRIMARY KEY,
            team_id INT NOT NULL,
            user_id INT NOT NULL,
            status VARCHAR(50) DEFAULT 'accepted',
            role VARCHAR(50) DEFAULT 'member',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(team_id, user_id)
        )
    ''')
    
    # Projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INT AUTO_INCREMENT PRIMARY KEY,
            team_id INT UNIQUE NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            github_url VARCHAR(500),
            demo_url VARCHAR(500),
            is_submitted BOOLEAN DEFAULT 0,
            submitted_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        )
    ''')
    
    # Jury assignments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jury_assignments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            hackathon_id INT NOT NULL,
            jury_id INT NOT NULL,
            FOREIGN KEY (hackathon_id) REFERENCES hackathons(id),
            FOREIGN KEY (jury_id) REFERENCES users(id),
            UNIQUE(hackathon_id, jury_id)
        )
    ''')
    
    # Evaluations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT NOT NULL,
            jury_id INT NOT NULL,
            innovation_score FLOAT,
            technical_score FLOAT,
            presentation_score FLOAT,
            usefulness_score FLOAT,
            overall_score FLOAT,
            comments TEXT,
            is_submitted BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (jury_id) REFERENCES users(id),
            UNIQUE(project_id, jury_id)
        )
    ''')
    
    db.commit()

    # Create sample data if database is empty
    cursor.execute('SELECT COUNT(*) as count FROM users')
    result = cursor.fetchone()
    if result['count'] == 0:
        create_sample_data(db)

    cursor.close()
    db.close()

def create_sample_data(db):
    """Create sample data for demonstration"""
    cursor = db.cursor()

    # Create users
    users = [
        ('organizer@hack.com', hash_password('password123'), 'John Organizer', 'organizer'),
        ('jury1@hack.com', hash_password('password123'), 'Jane Jury', 'jury'),
        ('participant1@hack.com', hash_password('password123'), 'Alice Developer', 'participant'),
        ('participant2@hack.com', hash_password('password123'), 'Bob Coder', 'participant'),
        ('participant3@hack.com', hash_password('password123'), 'Charlie Designer', 'participant'),
    ]

    for email, pwd_hash, name, role in users:
        cursor.execute(
            'INSERT INTO users (email, password_hash, full_name, role) VALUES (%s, %s, %s, %s)',
            (email, pwd_hash, name, role)
        )
    
    # Create a sample hackathon
    cursor.execute('''
        INSERT INTO hackathons (
            organizer_id, title, description, start_date, end_date,
            registration_deadline, status, is_online
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        1,  # organizer user id
        'AI Innovation Hackathon 2024',
        'Build the next generation of AI-powered applications. Join us for 48 hours of innovation, learning, and collaboration!',
        (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'),
        (datetime.now() + timedelta(days=9)).strftime('%Y-%m-%d %H:%M:%S'),
        (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
        'open_registration',
        1
    ))
    
    # Create a sample team
    cursor.execute('''
        INSERT INTO teams (hackathon_id, team_name, team_leader_id, description)
        VALUES (%s, %s, %s, %s)
    ''', (1, 'AI Innovators', 3, 'Building intelligent solutions for everyday problems'))

    # Add team member
    cursor.execute('''
        INSERT INTO team_members (team_id, user_id, role)
        VALUES (%s, %s, %s)
    ''', (1, 3, 'leader'))

    # Assign jury
    cursor.execute('''
        INSERT INTO jury_assignments (hackathon_id, jury_id)
        VALUES (%s, %s)
    ''', (1, 2))

    cursor.close()
    db.commit()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))

            db = get_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute('SELECT role FROM users WHERE id = %s', (session['user_id'],))
            user = cursor.fetchone()
            cursor.close()
            db.close()

            if not user or user['role'] != role:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes
@app.route('/')
def index():
    """Homepage"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get active hackathons
    cursor.execute('''
        SELECT h.*, u.full_name as organizer_name,
               (SELECT COUNT(*) FROM teams WHERE hackathon_id = h.id) as team_count
        FROM hackathons h
        JOIN users u ON h.organizer_id = u.id
        WHERE h.status IN ('open_registration', 'ongoing')
        ORDER BY h.start_date ASC
    ''')
    hackathons = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('index.html', hackathons=hackathons)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            'SELECT * FROM users WHERE email = %s AND password_hash = %s',
            (email, hash_password(password))
        )
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_role'] = user['role']
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'participant')

        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Check if email exists
        cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
        existing = cursor.fetchone()
        if existing:
            flash('Email already registered.', 'danger')
            cursor.close()
            db.close()
            return render_template('register.html')

        # Create user
        cursor.execute(
            'INSERT INTO users (email, password_hash, full_name, role) VALUES (%s, %s, %s, %s)',
            (email, hash_password(password), full_name, role)
        )
        db.commit()
        cursor.close()
        db.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    user_id = session['user_id']
    user_role = session['user_role']

    data = {}

    if user_role == 'organizer':
        # Get hackathons organized by user
        cursor.execute('''
            SELECT h.*,
                   (SELECT COUNT(*) FROM teams WHERE hackathon_id = h.id) as team_count,
                   (SELECT COUNT(*) FROM teams t
                    JOIN projects p ON t.id = p.team_id
                    WHERE t.hackathon_id = h.id AND p.is_submitted = 1) as submitted_count
            FROM hackathons h
            WHERE h.organizer_id = %s
            ORDER BY h.created_at DESC
        ''', (user_id,))
        data['hackathons'] = cursor.fetchall()

    elif user_role == 'jury':
        # Get assigned hackathons
        cursor.execute('''
            SELECT h.*,
                   (SELECT COUNT(*) FROM teams t
                    JOIN projects p ON t.id = p.team_id
                    WHERE t.hackathon_id = h.id AND p.is_submitted = 1) as total_projects,
                   (SELECT COUNT(*) FROM evaluations e
                    JOIN projects p ON e.project_id = p.id
                    JOIN teams t ON p.team_id = t.id
                    WHERE t.hackathon_id = h.id AND e.jury_id = %s AND e.is_submitted = 1) as evaluated_count
            FROM hackathons h
            JOIN jury_assignments ja ON h.id = ja.hackathon_id
            WHERE ja.jury_id = %s
            ORDER BY h.start_date DESC
        ''', (user_id, user_id))
        data['assignments'] = cursor.fetchall()

    else:  # participant
        # Get user's teams
        cursor.execute('''
            SELECT t.*, h.title as hackathon_title, h.status as hackathon_status,
                   (SELECT COUNT(*) FROM team_members WHERE team_id = t.id AND status = 'accepted') as member_count,
                   p.id as project_id, p.title as project_title, p.is_submitted
            FROM teams t
            JOIN hackathons h ON t.hackathon_id = h.id
            JOIN team_members tm ON t.id = tm.team_id
            LEFT JOIN projects p ON t.id = p.team_id
            WHERE tm.user_id = %s AND tm.status = 'accepted'
            ORDER BY t.created_at DESC
        ''', (user_id,))
        data['teams'] = cursor.fetchall()

        # Get pending join requests
        cursor.execute('''
            SELECT tm.id, tm.joined_at, tm.status, t.team_name, t.id as team_id, h.title as hackathon_title
            FROM team_members tm
            JOIN teams t ON tm.team_id = t.id
            JOIN hackathons h ON t.hackathon_id = h.id
            WHERE tm.user_id = %s AND tm.status IN ('pending', 'rejected')
            ORDER BY tm.joined_at DESC
        ''', (user_id,))
        data['join_requests'] = cursor.fetchall()

        # Get pending requests for teams user leads
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM team_members tm
            JOIN teams t ON tm.team_id = t.id
            WHERE t.team_leader_id = %s AND tm.status = 'pending'
        ''', (user_id,))
        result = cursor.fetchone()
        data['pending_team_requests'] = result['count'] if result else 0

    cursor.close()
    db.close()

    return render_template('dashboard.html', data=data)

@app.route('/hackathon/<int:id>')
def hackathon_detail(id):
    """Hackathon details page"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute('''
        SELECT h.*, u.full_name as organizer_name
        FROM hackathons h
        JOIN users u ON h.organizer_id = u.id
        WHERE h.id = %s
    ''', (id,))
    hackathon = cursor.fetchone()

    if not hackathon:
        flash('Hackathon not found.', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('index'))

    # Get teams
    cursor.execute('''
        SELECT t.*,
               u.full_name as leader_name,
               (SELECT COUNT(*) FROM team_members WHERE team_id = t.id) as member_count,
               p.is_submitted
        FROM teams t
        JOIN users u ON t.team_leader_id = u.id
        LEFT JOIN projects p ON t.id = p.team_id
        WHERE t.hackathon_id = %s
        ORDER BY t.created_at DESC
    ''', (id,))
    teams = cursor.fetchall()

    # Check if user is in a team
    user_team = None
    if 'user_id' in session:
        cursor.execute('''
            SELECT t.id, t.team_name
            FROM teams t
            JOIN team_members tm ON t.id = tm.team_id
            WHERE t.hackathon_id = %s AND tm.user_id = %s AND tm.status = 'accepted'
        ''', (id, session['user_id']))
        user_team = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template('hackathon_detail.html',
                         hackathon=hackathon,
                         teams=teams,
                         user_team=user_team)

@app.route('/hackathon/create', methods=['GET', 'POST'])
@role_required('organizer')
def create_hackathon():
    """Create new hackathon"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        registration_deadline = request.form.get('registration_deadline')
        max_team_size = int(request.form.get('max_team_size', 4))
        is_online = 1 if request.form.get('is_online') else 0

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('''
            INSERT INTO hackathons (
                organizer_id, title, description, start_date, end_date,
                registration_deadline, max_team_size, is_online, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'draft')
        ''', (session['user_id'], title, description, start_date, end_date,
              registration_deadline, max_team_size, is_online))
        db.commit()
        cursor.close()
        db.close()

        flash('Hackathon created successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('create_hackathon.html')

@app.route('/hackathon/<int:hackathon_id>/edit', methods=['GET', 'POST'])
@role_required('organizer')
def edit_hackathon(hackathon_id):
    """Edit hackathon (organizer only)"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Verify user is the organizer
    cursor.execute('''
        SELECT * FROM hackathons
        WHERE id = %s AND organizer_id = %s
    ''', (hackathon_id, session['user_id']))
    hackathon = cursor.fetchone()

    if not hackathon:
        flash('Only the organizer can edit this hackathon.', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        registration_deadline = request.form.get('registration_deadline')
        max_team_size = int(request.form.get('max_team_size', 4))
        is_online = 1 if request.form.get('is_online') else 0
        status = request.form.get('status')

        # Update hackathon
        cursor.execute('''
            UPDATE hackathons
            SET title = %s, description = %s, start_date = %s, end_date = %s,
                registration_deadline = %s, max_team_size = %s, is_online = %s, status = %s
            WHERE id = %s
        ''', (title, description, start_date, end_date, registration_deadline,
              max_team_size, is_online, status, hackathon_id))

        db.commit()
        cursor.close()
        db.close()

        flash('Hackathon updated successfully!', 'success')
        return redirect(url_for('hackathon_detail', id=hackathon_id))

    cursor.close()
    db.close()

    return render_template('edit_hackathon.html', hackathon=hackathon)

@app.route('/team/create/<int:hackathon_id>', methods=['GET', 'POST'])
@login_required
def create_team(hackathon_id):
    """Create a new team"""
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        description = request.form.get('description')

        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Check if user already in a team for this hackathon
        cursor.execute('''
            SELECT t.id FROM teams t
            JOIN team_members tm ON t.id = tm.team_id
            WHERE t.hackathon_id = %s AND tm.user_id = %s
        ''', (hackathon_id, session['user_id']))
        existing = cursor.fetchone()

        if existing:
            flash('You are already in a team for this hackathon.', 'warning')
            cursor.close()
            db.close()
            return redirect(url_for('hackathon_detail', id=hackathon_id))

        # Create team
        cursor.execute('''
            INSERT INTO teams (hackathon_id, team_name, team_leader_id, description)
            VALUES (%s, %s, %s, %s)
        ''', (hackathon_id, team_name, session['user_id'], description))

        team_id = cursor.lastrowid

        # Add leader as member
        cursor.execute('''
            INSERT INTO team_members (team_id, user_id, role)
            VALUES (%s, %s, 'leader')
        ''', (team_id, session['user_id']))

        db.commit()
        cursor.close()
        db.close()

        flash('Team created successfully!', 'success')
        return redirect(url_for('team_detail', id=team_id))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM hackathons WHERE id = %s', (hackathon_id,))
    hackathon = cursor.fetchone()
    cursor.close()
    db.close()

    return render_template('create_team.html', hackathon=hackathon)

@app.route('/team/<int:id>')
@login_required
def team_detail(id):
    """Team details page"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute('''
        SELECT t.*, h.title as hackathon_title, h.id as hackathon_id,
               u.full_name as leader_name
        FROM teams t
        JOIN hackathons h ON t.hackathon_id = h.id
        JOIN users u ON t.team_leader_id = u.id
        WHERE t.id = %s
    ''', (id,))
    team = cursor.fetchone()

    if not team:
        flash('Team not found.', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('index'))

    # Get team members
    cursor.execute('''
        SELECT u.full_name, u.email, u.github_username, tm.role
        FROM team_members tm
        JOIN users u ON tm.user_id = u.id
        WHERE tm.team_id = %s AND tm.status = 'accepted'
    ''', (id,))
    members = cursor.fetchall()

    # Get project
    cursor.execute('''
        SELECT * FROM projects WHERE team_id = %s
    ''', (id,))
    project = cursor.fetchone()

    # Check if user is team leader
    is_leader = (team['team_leader_id'] == session['user_id'])

    cursor.close()
    db.close()

    return render_template('team_detail.html',
                         team=team,
                         members=members,
                         project=project,
                         is_leader=is_leader)

@app.route('/team/<int:team_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_team(team_id):
    """Edit team information (leader only)"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Verify user is team leader
    cursor.execute('''
        SELECT t.*, h.title as hackathon_title, h.id as hackathon_id
        FROM teams t
        JOIN hackathons h ON t.hackathon_id = h.id
        WHERE t.id = %s AND t.team_leader_id = %s
    ''', (team_id, session['user_id']))
    team = cursor.fetchone()

    if not team:
        flash('Only team leader can edit team information.', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        team_name = request.form.get('team_name')
        description = request.form.get('description')

        # Check if new team name is unique within the hackathon
        cursor.execute('''
            SELECT id FROM teams
            WHERE hackathon_id = %s AND team_name = %s AND id != %s
        ''', (team['hackathon_id'], team_name, team_id))
        existing = cursor.fetchone()

        if existing:
            flash('A team with this name already exists in this hackathon.', 'danger')
            cursor.close()
            db.close()
            return render_template('edit_team.html', team=team)

        # Update team information
        cursor.execute('''
            UPDATE teams
            SET team_name = %s, description = %s
            WHERE id = %s
        ''', (team_name, description, team_id))

        db.commit()
        cursor.close()
        db.close()

        flash('Team information updated successfully!', 'success')
        return redirect(url_for('team_detail', id=team_id))

    cursor.close()
    db.close()

    return render_template('edit_team.html', team=team)

@app.route('/team/<int:team_id>/join', methods=['POST'])
@login_required
def request_join_team(team_id):
    """Send a request to join a team"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get team info
    cursor.execute('SELECT hackathon_id, team_name FROM teams WHERE id = %s', (team_id,))
    team = cursor.fetchone()

    if not team:
        flash('Team not found.', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('index'))

    # Check if user already has a request or membership
    cursor.execute('''
        SELECT status FROM team_members
        WHERE team_id = %s AND user_id = %s
    ''', (team_id, session['user_id']))
    existing = cursor.fetchone()

    if existing:
        if existing['status'] == 'accepted':
            flash('You are already a member of this team.', 'warning')
        elif existing['status'] == 'pending':
            flash('You already have a pending request for this team.', 'warning')
        elif existing['status'] == 'rejected':
            flash('Your previous request was rejected.', 'warning')
        cursor.close()
        db.close()
        return redirect(url_for('hackathon_detail', id=team['hackathon_id']))

    # Check if user is already in another team for this hackathon
    cursor.execute('''
        SELECT t.team_name FROM teams t
        JOIN team_members tm ON t.id = tm.team_id
        WHERE t.hackathon_id = %s AND tm.user_id = %s AND tm.status = 'accepted'
    ''', (team['hackathon_id'], session['user_id']))
    other_team = cursor.fetchone()

    if other_team:
        flash(f'You are already in team "{other_team["team_name"]}" for this hackathon.', 'warning')
        cursor.close()
        db.close()
        return redirect(url_for('hackathon_detail', id=team['hackathon_id']))

    # Create join request
    cursor.execute('''
        INSERT INTO team_members (team_id, user_id, status, role)
        VALUES (%s, %s, 'pending', 'member')
    ''', (team_id, session['user_id']))

    db.commit()
    cursor.close()
    db.close()

    flash(f'Join request sent to team "{team["team_name"]}"!', 'success')
    return redirect(url_for('hackathon_detail', id=team['hackathon_id']))

@app.route('/team/<int:team_id>/requests')
@login_required
def view_team_requests(team_id):
    """View pending join requests for a team"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Verify user is team leader
    cursor.execute('''
        SELECT t.*, h.title as hackathon_title
        FROM teams t
        JOIN hackathons h ON t.hackathon_id = h.id
        WHERE t.id = %s AND t.team_leader_id = %s
    ''', (team_id, session['user_id']))
    team = cursor.fetchone()

    if not team:
        flash('Only team leader can view requests.', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('dashboard'))

    # Get pending requests
    cursor.execute('''
        SELECT tm.id, tm.user_id, tm.joined_at, u.full_name, u.email, u.github_username, u.bio
        FROM team_members tm
        JOIN users u ON tm.user_id = u.id
        WHERE tm.team_id = %s AND tm.status = 'pending'
        ORDER BY tm.joined_at ASC
    ''', (team_id,))
    requests = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('team_requests.html', team=team, requests=requests)

@app.route('/team/request/<int:request_id>/approve', methods=['POST'])
@login_required
def approve_team_request(request_id):
    """Approve a team join request"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get request and verify user is team leader
    cursor.execute('''
        SELECT tm.*, t.team_leader_id, t.hackathon_id
        FROM team_members tm
        JOIN teams t ON tm.team_id = t.id
        WHERE tm.id = %s AND tm.status = 'pending'
    ''', (request_id,))
    request_data = cursor.fetchone()

    if not request_data:
        flash('Request not found.', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('dashboard'))

    if request_data['team_leader_id'] != session['user_id']:
        flash('Only team leader can approve requests.', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('dashboard'))

    # Approve the request
    cursor.execute('''
        UPDATE team_members
        SET status = 'accepted'
        WHERE id = %s
    ''', (request_id,))

    db.commit()
    cursor.close()
    db.close()

    flash('Team member approved!', 'success')
    return redirect(url_for('view_team_requests', team_id=request_data['team_id']))

@app.route('/team/request/<int:request_id>/reject', methods=['POST'])
@login_required
def reject_team_request(request_id):
    """Reject a team join request"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get request and verify user is team leader
    cursor.execute('''
        SELECT tm.*, t.team_leader_id
        FROM team_members tm
        JOIN teams t ON tm.team_id = t.id
        WHERE tm.id = %s AND tm.status = 'pending'
    ''', (request_id,))
    request_data = cursor.fetchone()

    if not request_data:
        flash('Request not found.', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('dashboard'))

    if request_data['team_leader_id'] != session['user_id']:
        flash('Only team leader can reject requests.', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('dashboard'))

    # Reject the request
    cursor.execute('''
        UPDATE team_members
        SET status = 'rejected'
        WHERE id = %s
    ''', (request_id,))

    db.commit()
    cursor.close()
    db.close()

    flash('Request rejected.', 'info')
    return redirect(url_for('view_team_requests', team_id=request_data['team_id']))

@app.route('/project/submit/<int:team_id>', methods=['GET', 'POST'])
@login_required
def submit_project(team_id):
    """Submit project for team"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Verify user is team leader
    cursor.execute(
        'SELECT * FROM teams WHERE id = %s AND team_leader_id = %s',
        (team_id, session['user_id'])
    )
    team = cursor.fetchone()

    if not team:
        flash('Only team leader can submit project.', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        github_url = request.form.get('github_url')
        demo_url = request.form.get('demo_url')
        is_submitted = 1 if request.form.get('submit') else 0

        # Check if project exists
        cursor.execute('SELECT id FROM projects WHERE team_id = %s', (team_id,))
        existing = cursor.fetchone()

        if existing:
            # Update existing project
            cursor.execute('''
                UPDATE projects
                SET title = %s, description = %s, github_url = %s, demo_url = %s,
                    is_submitted = %s, submitted_at = %s
                WHERE team_id = %s
            ''', (title, description, github_url, demo_url, is_submitted,
                  datetime.now() if is_submitted else None, team_id))
        else:
            # Create new project
            cursor.execute('''
                INSERT INTO projects (team_id, title, description, github_url, demo_url, is_submitted, submitted_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (team_id, title, description, github_url, demo_url, is_submitted,
                  datetime.now() if is_submitted else None))

        db.commit()
        cursor.close()
        db.close()

        if is_submitted:
            flash('Project submitted successfully!', 'success')
        else:
            flash('Project saved as draft.', 'info')

        return redirect(url_for('team_detail', id=team_id))

    # Get existing project if any
    cursor.execute('SELECT * FROM projects WHERE team_id = %s', (team_id,))
    project = cursor.fetchone()
    cursor.close()
    db.close()

    return render_template('submit_project.html', team=team, project=project)

@app.route('/evaluate/<int:hackathon_id>')
@role_required('jury')
def evaluate_hackathon(hackathon_id):
    """View projects to evaluate"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get submitted projects
    cursor.execute('''
        SELECT p.*, t.team_name,
               (SELECT COUNT(*) FROM evaluations
                WHERE project_id = p.id AND jury_id = %s AND is_submitted = 1) as is_evaluated
        FROM projects p
        JOIN teams t ON p.team_id = t.id
        WHERE t.hackathon_id = %s AND p.is_submitted = 1
        ORDER BY p.submitted_at DESC
    ''', (session['user_id'], hackathon_id))
    projects = cursor.fetchall()

    cursor.execute('SELECT * FROM hackathons WHERE id = %s', (hackathon_id,))
    hackathon = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template('evaluate_list.html', projects=projects, hackathon=hackathon)

@app.route('/evaluate/project/<int:project_id>', methods=['GET', 'POST'])
@role_required('jury')
def evaluate_project(project_id):
    """Evaluate a specific project"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute('''
        SELECT p.*, t.team_name, t.id as team_id
        FROM projects p
        JOIN teams t ON p.team_id = t.id
        WHERE p.id = %s
    ''', (project_id,))
    project = cursor.fetchone()

    if not project:
        flash('Project not found.', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        innovation = float(request.form.get('innovation'))
        technical = float(request.form.get('technical'))
        presentation = float(request.form.get('presentation'))
        usefulness = float(request.form.get('usefulness'))
        comments = request.form.get('comments')
        is_submitted = 1 if request.form.get('submit') else 0

        overall = (innovation + technical + presentation + usefulness) / 4.0

        # Check if evaluation exists
        cursor.execute('''
            SELECT id FROM evaluations
            WHERE project_id = %s AND jury_id = %s
        ''', (project_id, session['user_id']))
        existing = cursor.fetchone()

        if existing:
            cursor.execute('''
                UPDATE evaluations
                SET innovation_score = %s, technical_score = %s,
                    presentation_score = %s, usefulness_score = %s,
                    overall_score = %s, comments = %s, is_submitted = %s
                WHERE id = %s
            ''', (innovation, technical, presentation, usefulness,
                  overall, comments, is_submitted, existing['id']))
        else:
            cursor.execute('''
                INSERT INTO evaluations (
                    project_id, jury_id, innovation_score, technical_score,
                    presentation_score, usefulness_score, overall_score,
                    comments, is_submitted
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (project_id, session['user_id'], innovation, technical,
                  presentation, usefulness, overall, comments, is_submitted))

        db.commit()
        cursor.close()
        db.close()

        if is_submitted:
            flash('Evaluation submitted successfully!', 'success')
        else:
            flash('Evaluation saved as draft.', 'info')

        return redirect(url_for('dashboard'))

    # Get existing evaluation
    cursor.execute('''
        SELECT * FROM evaluations
        WHERE project_id = %s AND jury_id = %s
    ''', (project_id, session['user_id']))
    evaluation = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template('evaluate_project.html', project=project, evaluation=evaluation)

@app.route('/rankings/<int:hackathon_id>')
def view_rankings(hackathon_id):
    """View hackathon rankings"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute('SELECT * FROM hackathons WHERE id = %s', (hackathon_id,))
    hackathon = cursor.fetchone()

    # Calculate rankings
    cursor.execute('''
        SELECT
            t.team_name,
            p.title as project_title,
            p.github_url,
            p.demo_url,
            AVG(e.overall_score) as final_score,
            COUNT(e.id) as evaluation_count
        FROM projects p
        JOIN teams t ON p.team_id = t.id
        LEFT JOIN evaluations e ON p.id = e.project_id AND e.is_submitted = 1
        WHERE t.hackathon_id = %s AND p.is_submitted = 1
        GROUP BY p.id
        HAVING COUNT(e.id) > 0
        ORDER BY final_score DESC
    ''', (hackathon_id,))
    rankings = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('rankings.html', hackathon=hackathon, rankings=rankings)

if __name__ == '__main__':
    # Initialize database tables
    try:
        init_db()
    except Error as e:
        print(f"Database initialization error: {e}")
        print(f"Please ensure MySQL is running and database '{app.config['DB_NAME']}' exists")
        print(f"You can create it with: CREATE DATABASE {app.config['DB_NAME']};")

    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
