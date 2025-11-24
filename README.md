CommitGuardian

CommitGuardian is a distributed web application designed to help developers maintain their GitHub contribution streaks. It monitors daily activity using the GitHub API and provides an automated alert system via email if no contributions are detected, offering a streamlined mechanism to push a maintenance commit to preserve the streak.

Project Overview

The application operates on a client-server architecture designed for distributed infrastructure. It solves the problem of broken coding streaks by automating the verification process and providing a quick-action dashboard for remediation.

Architecture

Backend: Built with Python's native http.server and socketserver libraries to handle HTTP requests, manage sessions, and interact with external APIs efficiently with zero external dependencies.

Frontend: Developed with HTML5, CSS3, and Vanilla JavaScript, communicating with the backend via a RESTful internal API.

Data Persistence: Utilizes a flat-file JSON database (users.json) for lightweight token and setting storage.

Infrastructure: Deployed across high-availability application servers (Web-01, Web-02) behind an Nginx Load Balancer (Lb-01), serving traffic via the domain streak.bterance.tech.

Technical Stack

Language: Python 3.x

Frontend: HTML, CSS, JavaScript

Server: Nginx (Reverse Proxy & Load Balancer)

Process Management: Systemd

APIs:

GitHub REST API: For fetching commit history and user events.

GitHub OAuth: For secure user authentication.

SMTP: For sending email notifications via Gmail.

Features

OAuth Authentication: Secure user login using GitHub credentials with a custom OAuth implementation.

Activity Dashboard: Real-time visualization of current contribution streaks and last push activity.

Automated Scheduler: A background cron job runs nightly to verify activity for all registered users.

Email Alerts: Automated email notifications containing direct remediation links when inactivity is detected.

Streak Rescue: One-click trigger to push a maintenance commit to a dedicated repository directly from the dashboard.

Developer Controls: Integrated simulation mode for testing UI states and alert workflows.

Installation

Prerequisites

Python 3.10 or higher

A GitHub OAuth App (Client ID and Secret)

A Gmail account with an App Password

Local Setup

Clone the repository:

git clone [https://github.com/terancebana/Commit-Guardian.git](https://github.com/terancebana/Commit-Guardian.git)
cd Commit-Guardian


Configure Environment Variables:
Create a file at server/data/.env:

GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
BASE_URL=http://localhost:8000
JUNK_REPO_NAME=daily-activity-log
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password


Start the Server:

python3 server/backend/server.py


Access the application at http://localhost:8000.

Deployment Guide

This application is deployed using a Round Robin load balancing strategy for high availability.

1. Application Servers (Web-01 & Web-02)

Both servers run an identical instance of the application managed by systemd.

Path: /home/ubuntu/Commit-Guardian

Service: commitguardian.service

Command: /usr/bin/python3 /home/ubuntu/Commit-Guardian/server/backend/server.py

To update the application on the servers:

git pull origin main
sudo systemctl restart commitguardian


2. Load Balancer (Lb-01)

Nginx is configured to distribute traffic evenly between the two application servers.

Configuration Snippet:

upstream backend {
    server <WEB-01-IP>:8000;
    server <WEB-02-IP>:8000;
}

server {
    listen 80;
    server_name streak.bterance.tech;
    location / {
        proxy_pass http://backend;
        # ... proxy headers ...
    }
}


API Reference

The backend exposes the following endpoints:

GET /login: Initiates the GitHub OAuth flow.

GET /api/status: Returns the current user's streak status JSON.

POST /api/push-junk: Triggers the creation of a commit in the target repository.

Authors

CYUZUZO BANA TERANCE