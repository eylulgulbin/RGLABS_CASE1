Hackathon Platform 

A complete hackathon management platform built with Python Flask.

Prerequisites

- **Python 3.7+** installed on your system
- **VSCode** (Visual Studio Code)
- **Git** (optional, for version control)


Run the Application

Using Terminal
```bash
python app.py
```

Step 4: Open in Browser

Navigate to: **http://localhost:5000**

You should see the Hackathon Platform homepage

Demo Accounts

Login with these pre-created accounts:

### Organizer Account
```
Email: organizer@hack.com
Password: password123
```

### Jury Account
```
Email: jury1@hack.com
Password: password123
```

### Participant Account
```
Email: participant1@hack.com
Password: password123
```

## 📁 Project Structure

```
hackathon-platform-vscode/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── .vscode/                 # VSCode settings
│   ├── settings.json        # Editor settings
│   └── launch.json          # Debug configurations
└── templates/               # HTML templates
    ├── base.html           # Base template
    ├── index.html          # Homepage
    ├── login.html          # Login page
    ├── register.html       # Registration
    ├── dashboard.html      # User dashboard
    ├── hackathon_detail.html
    ├── create_hackathon.html
    ├── create_team.html
    ├── team_detail.html
    ├── submit_project.html
    ├── evaluate_list.html
    ├── evaluate_project.html
    └── rankings.html
```

## 🎯 Features

### For Organizers
- ✅ Create and manage hackathons
- ✅ Set dates, rules, and team size limits
- ✅ Assign jury members
- ✅ View all submissions
- ✅ Publish rankings

### For Participants
- ✅ Browse and join hackathons
- ✅ Create or join teams
- ✅ Submit projects with GitHub/demo links
- ✅ View final rankings

### For Jury
- ✅ View assigned hackathons
- ✅ Evaluate projects on 4 criteria
- ✅ Provide detailed feedback
- ✅ View all evaluations

## 🛠️ Development Tips

### Using VSCode Features

1. **IntelliSense**: Auto-completion works for Flask, Python
2. **Debugging**: Set breakpoints by clicking left of line numbers
3. **Terminal**: Integrated terminal (Ctrl+` or View → Terminal)
4. **Extensions**: Install these for better experience:
   - Python (Microsoft)
   - Pylance
   - Flask Snippets
   - Jinja (for template syntax)

### Debugging

1. Set breakpoints in `app.py`
2. Press `F5` to start debugging
3. Use Debug Console to inspect variables
4. Step through code with F10/F11

### Hot Reload

The app runs in debug mode by default:
- Save any file to see changes immediately
- Browser auto-refreshes on template changes
- Server auto-restarts on code changes

## 🗄️ Database

The application uses **SQLite** (file-based database):
- Database file: `hackathon.db` (created automatically)
- Sample data pre-loaded on first run
- View with SQLite extensions in VSCode

### Reset Database

If you need to start fresh:

```bash
# Stop the app (Ctrl+C)
# Delete the database
rm hackathon.db  # On Mac/Linux
del hackathon.db  # On Windows

# Restart the app
python app.py
```

## 📝 Making Changes

### Add a New Page

1. Create route in `app.py`:
```python
@app.route('/my-page')
def my_page():
    return render_template('my_page.html')
```

2. Create template in `templates/my_page.html`:
```html
{% extends "base.html" %}
{% block content %}
<h1>My New Page</h1>
{% endblock %}
```

### Modify Styling

All CSS is in `templates/base.html` in the `<style>` section.
Change colors, fonts, layouts as needed!

### Add Database Table

Edit the `init_db()` function in `app.py`:
```python
db.execute('''
    CREATE TABLE IF NOT EXISTS my_table (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
''')
```

## 🔧 Troubleshooting

### Issue: Module not found

**Solution:**
```bash
# Make sure virtual environment is activated
# You should see (venv) in your terminal

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Port 5000 already in use

**Solution:**
Edit `app.py`, last line:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```
Then access at `http://localhost:5001`

### Issue: Database locked

**Solution:**
```bash
# Stop the app completely (Ctrl+C)
# Delete database and restart
rm hackathon.db
python app.py
```

### Issue: Templates not loading

**Solution:**
- Make sure `templates/` folder is in same directory as `app.py`
- Check file names match exactly (case-sensitive)
- Restart Flask server

## 🚢 Deployment

### For Production

1. **Change Secret Key** in `app.py`:
```python
app.secret_key = 'your-super-secret-production-key'
```

2. **Use Production Database** (PostgreSQL):
```python
app.config['DATABASE'] = 'postgresql://user:pass@host/db'
```

3. **Disable Debug Mode**:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

4. **Use Production Server** (Gunicorn):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Deploy to Cloud

- **Heroku**: Use Procfile
- **AWS**: Use Elastic Beanstalk
- **DigitalOcean**: Use App Platform
- **Google Cloud**: Use App Engine

## 📚 Learning Resources

### Flask Documentation
- Official Docs: https://flask.palletsprojects.com/
- Tutorial: https://flask.palletsprojects.com/tutorial/

### Python Resources
- Python.org: https://docs.python.org/3/
- Real Python: https://realpython.com/

### SQLite
- SQLite Tutorial: https://www.sqlitetutorial.net/

## 🎓 Next Steps

1. **Explore the code**: Start with `app.py` and read through
2. **Test all features**: Login as different users
3. **Modify and experiment**: Change colors, add features
4. **Add your own features**: Notifications, chat, file uploads
5. **Deploy online**: Share with others!

## 🐛 Known Limitations

This is a **prototype/demo application**. For production:
- ❌ Passwords are SHA-256 (use bcrypt instead)
- ❌ No email verification
- ❌ No password reset
- ❌ No file uploads
- ❌ No real-time features
- ❌ Basic CSRF protection only

## 📄 License

MIT License - Free to use, modify, and distribute!

## 🤝 Support

Having issues? 
1. Check Troubleshooting section above
2. Read error messages carefully
3. Google the error (Stack Overflow is your friend!)
4. Check VSCode's Problems panel (Ctrl+Shift+M)

## 🎉 Have Fun!

You're ready to start hacking! Explore, break things, and learn.

**Happy Coding! 🚀**

---

**Quick Commands:**
```bash
# Start development
python app.py

# Install dependencies
pip install -r requirements.txt

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Mac/Linux)
source venv/bin/activate

# View all routes
python -c "from app import app; print(app.url_map)"
```
