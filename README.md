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

Open in Browser

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

Features

For Organizers
- Create and manage hackathons
- Set dates, rules, and team size limits
- Assign jury members
- View all submissions
- Publish rankings

For Participants
- Browse and join hackathons
- Create or join teams
- Submit projects with GitHub/demo links
- View final rankings

For Jury
- View assigned hackathons
- Evaluate projects on 4 criteria
- Provide detailed feedback
- View all evaluations

