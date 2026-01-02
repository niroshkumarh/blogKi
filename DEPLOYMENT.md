# HORIZON Blog - Ubuntu Deployment Guide

## Prerequisites
- Ubuntu Server (20.04 LTS or later)
- Python 3.9+
- Nginx
- Git

## Step 1: System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx git

# Create application user
sudo useradd -m -s /bin/bash blogsite
```

## Step 2: Application Setup

```bash
# Switch to blogsite user
sudo su - blogsite

# Clone repository
git clone https://github.com/niroshkumarh/blogKi.git
cd blogKi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Environment Configuration

Create `/home/blogsite/blogKi/.env`:

```bash
# Flask Configuration
SECRET_KEY=generate-a-strong-random-key-here
FLASK_ENV=production

# Database
DATABASE_URL=sqlite:////var/lib/blogsite/blogsite.db

# Microsoft Entra ID
CLIENT_ID=423dd38a-439a-4b99-a313-9472d2c0dad6
CLIENT_SECRET=YOUR_NEW_CLIENT_SECRET_HERE
TENANT_ID=6b8b8296-bdff-4ad8-93ad-84bcbf3842f5
REDIRECT_URI=http://YOUR_SERVER_IP/auth/callback

# Admin Configuration
ADMIN_EMAILS=your-email@domain.com
```

**Important**: Replace `YOUR_NEW_CLIENT_SECRET_HERE` and `YOUR_SERVER_IP` with actual values.

## Step 4: Database Setup

```bash
# Create database directory
sudo mkdir -p /var/lib/blogsite
sudo chown blogsite:blogsite /var/lib/blogsite

# Initialize database
cd /home/blogsite/blogKi
source venv/bin/activate
python3 init_db.py
```

## Step 5: Systemd Service

Create `/etc/systemd/system/blogsite.service`:

```ini
[Unit]
Description=HORIZON Blog (Gunicorn)
After=network.target

[Service]
Type=notify
User=blogsite
Group=blogsite
WorkingDirectory=/home/blogsite/blogKi
Environment="PATH=/home/blogsite/blogKi/venv/bin"
EnvironmentFile=/home/blogsite/blogKi/.env
ExecStart=/home/blogsite/blogKi/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 120 app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable blogsite
sudo systemctl start blogsite
sudo systemctl status blogsite
```

## Step 6: Nginx Configuration

Create `/etc/nginx/sites-available/blogsite`:

```nginx
server {
    listen 80;
    server_name YOUR_SERVER_IP;
    
    client_max_body_size 20M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    
    location /assets {
        alias /home/blogsite/blogKi/assets;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /uploads {
        alias /home/blogsite/blogKi/uploads;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/blogsite /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Step 7: Entra ID App Configuration

In Azure Portal > App registrations > BlogSite:

1. **Redirect URIs**: Add `http://YOUR_SERVER_IP/auth/callback`
2. **Logout URL**: Add `http://YOUR_SERVER_IP`
3. **Supported account types**: Single tenant (your organization only)

## Step 8: Initialize with Existing Posts

Run the migration script to import your existing 2 blog posts:

```bash
cd /home/blogsite/blogKi
source venv/bin/activate
python3 migrate_existing_posts.py
```

## Maintenance Commands

```bash
# View logs
sudo journalctl -u blogsite -f

# Restart service
sudo systemctl restart blogsite

# Pull updates
sudo su - blogsite
cd /home/blogsite/blogKi
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart blogsite
```

## Security Recommendations

1. **Use HTTPS**: Set up Let's Encrypt SSL certificate
2. **Firewall**: Configure UFW to allow only 80, 443, and SSH
3. **Regular Updates**: Keep system and dependencies updated
4. **Backup Database**: Regular backups of `/var/lib/blogsite/blogsite.db`
5. **Rotate Secrets**: Rotate Entra ID client secret annually

## Troubleshooting

- **500 errors**: Check logs with `sudo journalctl -u blogsite -n 100`
- **Auth fails**: Verify `.env` file has correct Entra ID credentials
- **Static files 404**: Check Nginx config and file permissions
- **Database locked**: Ensure only one gunicorn process is running


