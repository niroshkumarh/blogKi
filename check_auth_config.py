"""Check authentication configuration"""
from app import app

with app.app_context():
    print("=== Authentication Configuration ===")
    print(f"CLIENT_ID: {app.config['ENTRA_CLIENT_ID']}")
    print(f"CLIENT_SECRET: {'*' * 20 + app.config['ENTRA_CLIENT_SECRET'][-4:] if app.config['ENTRA_CLIENT_SECRET'] else 'NOT SET'}")
    print(f"TENANT_ID: {app.config['ENTRA_TENANT_ID']}")
    print(f"REDIRECT_URI: {app.config['ENTRA_REDIRECT_URI']}")
    print(f"ADMIN_EMAILS: {app.config['ADMIN_EMAILS']}")
    print("\n=== What to Check in Azure Portal ===")
    print("1. Go to: Azure Portal > App registrations > Your app")
    print("2. Click 'Authentication' on the left")
    print("3. Under 'Platform configurations' > 'Web', verify redirect URIs include:")
    print(f"   - {app.config['ENTRA_REDIRECT_URI']}")
    print("\n4. Under 'Supported account types', it should be:")
    print("   - 'Accounts in this organizational directory only (Single tenant)'")


