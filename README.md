# CommitGuardian 

Short tagline: "A small tool to remind developers to push daily and optionally automate safe commits."

## Project Overview
Explain in 2–3 sentences the problem you solve, your approach, and the main user flow.

## Features
- Nightly check if a user pushed any commits to a repo (uses GitHub API)
- Sends a reminder notification if nothing was pushed today
- Optionally (with user consent) creates 1–6 harmless commits and pushes to the repo
- Web dashboard to review status and accept auto-push
- Deployed on two web servers behind a load balancer (Web01, Web02, Lb01)

## Tech Stack
- Frontend: HTML, CSS, Vanilla JS (Fetch API, Notification API)
- Backend: Python 3.x (no web framework; `http.server` / `http.client`)
- APIs: GitHub REST API, Web Push (VAPID)
- Deployment: Nginx on Ubuntu, cron, Git
- Note: All APIs used are free or have free tiers. No external web frameworks used.

## Installation (local)
1. Clone:
    git clone git@github.com/terancebana/Commit-Guardian.git
    cd Commit-Guardian

2. Create `.env` from `.env.example` and fill values:
- `GITHUB_TOKEN=...` (optional but recommended for rate limits)
- `VAPID_PUBLIC_KEY=...` (if using web push)
- `VAPID_PRIVATE_KEY=...`
- `NOTIFICATION_EMAIL=...` (optional)
3. Start backend:
- (explain exactly how you start `server.py` with python and env vars)
4. Open `frontend/index.html` in your browser and follow setup instructions.

## Deployment (Web01 / Web02 & Lb01)
Explain:
- How to copy code to servers (git clone)
- How to install Python version and dependencies if any
- How to create system cron job (example crontab entry)
- How to configure Nginx on Lb01 to reverse-proxy and balance between Web01 and Web02 (include `upstream` config snippet)
- How to start your backend as a service (use `systemd` unit or a simple `nohup python server.py &` for demo — but `systemd` is preferred for production-like behavior)
- Provide exact commands you used during deployment and any modifications to firewall/ports.

## How it works (architecture)
- Diagram (or explanation) of frontend ↔ backend ↔ GitHub API ↔ local git automation  
- Explain the “evening check” cron job logic and user consent flow

## API usage & endpoints
- Document backend endpoints (e.g., `/api/status?owner=...&repo=...`, `/api/request_push`, `/api/approve_push`)
- Show example request/response JSON for each endpoint
- Include rate limit considerations and caching strategy

## Security
- Explain how you store secrets (no secrets in repo)
- Explain the GitHub token permissions needed (scopes)
- Explain VAPID key usage and secure storage
- Mention best practices for production (rotate tokens, limit scopes)

## Testing
- Manual tests you performed
- How to run unit tests for modules (if any)
- How to simulate edge cases (network failure, push conflict)

## Challenges & Future Work
- Things that gave you trouble and how you solved them
- Optional extensions (Docker, OAuth login, CI/CD, advanced scheduler)

## Credits
- GitHub API docs: https://docs.github.com/en/rest
- Web Push docs: https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API

## Demo video
- Link to your demo hosted on YouTube (<= 2 minutes)
- Brief description of what the video shows

## License
- Your chosen license (MIT recommended)
