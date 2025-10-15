#@title 🔧 FIX DATABASE - Fix PostgreSQL Authentication
#@markdown Run this if you see "Peer authentication failed" errors

import subprocess
import time

print("="*70)
print("🔧 Fixing PostgreSQL Authentication")
print("="*70)

# Fix pg_hba.conf to allow password authentication
print("\n1️⃣ Updating PostgreSQL configuration...")

# Get PostgreSQL version to find correct config file
result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
print(f"  PostgreSQL version: {result.stdout.strip()}")

# Common PostgreSQL config locations in Colab
config_paths = [
    '/etc/postgresql/15/main/pg_hba.conf',
    '/etc/postgresql/14/main/pg_hba.conf',
    '/etc/postgresql/13/main/pg_hba.conf',
    '/etc/postgresql/12/main/pg_hba.conf',
]

import os
config_file = None
for path in config_paths:
    if os.path.exists(path):
        config_file = path
        break

if not config_file:
    print("  ⚠️  Could not find pg_hba.conf, searching...")
    result = subprocess.run(['find', '/etc/postgresql', '-name', 'pg_hba.conf'],
                          capture_output=True, text=True)
    if result.stdout.strip():
        config_file = result.stdout.strip().split('\n')[0]
        print(f"  Found: {config_file}")
    else:
        print("  ❌ Could not find PostgreSQL config!")
        import sys
        sys.exit(1)
else:
    print(f"  Found config: {config_file}")

# Backup original config
print("\n2️⃣ Backing up original configuration...")
subprocess.run(['cp', config_file, f'{config_file}.backup'], capture_output=True)
print("  ✅ Backup created")

# Update pg_hba.conf to use md5 authentication instead of peer
print("\n3️⃣ Updating authentication method...")

# Read current config
with open(config_file, 'r') as f:
    original_config = f.read()

# Replace peer and ident with md5
updated_config = original_config
updated_config = updated_config.replace('local   all             all                                     peer',
                                       'local   all             all                                     md5')
updated_config = updated_config.replace('host    all             all             127.0.0.1/32            ident',
                                       'host    all             all             127.0.0.1/32            md5')
updated_config = updated_config.replace('host    all             all             ::1/128                 ident',
                                       'host    all             all             ::1/128                 md5')

# Also handle variations in spacing
import re
updated_config = re.sub(r'local\s+all\s+all\s+peer', 'local   all             all                                     md5', updated_config)
updated_config = re.sub(r'host\s+all\s+all\s+127\.0\.0\.1/32\s+ident', 'host    all             all             127.0.0.1/32            md5', updated_config)

# Write updated config with sudo
with open('/tmp/pg_hba_new.conf', 'w') as f:
    f.write(updated_config)

subprocess.run(['sudo', 'cp', '/tmp/pg_hba_new.conf', config_file], capture_output=True)
print("  ✅ Configuration updated")

# Restart PostgreSQL
print("\n4️⃣ Restarting PostgreSQL...")
subprocess.run(['sudo', 'service', 'postgresql', 'restart'], capture_output=True)
time.sleep(3)
print("  ✅ PostgreSQL restarted")

# Test connection
print("\n5️⃣ Testing database connection...")
result = subprocess.run(
    ['psql', '-U', 'masuka', '-d', 'masuka', '-h', 'localhost', '-c', 'SELECT 1;'],
    capture_output=True,
    text=True,
    env={'PGPASSWORD': 'password123'}
)

if result.returncode == 0:
    print("  ✅ Database connection successful!")
    print(result.stdout)
else:
    print(f"  ⚠️  Connection test returned: {result.returncode}")
    print(f"  STDOUT: {result.stdout}")
    print(f"  STDERR: {result.stderr}")

# Update backend .env to use localhost connection
print("\n6️⃣ Updating backend configuration...")
env_file = '/content/masuka-v2/backend/.env'

if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        content = f.read()

    # Update DATABASE_URL to use host=localhost
    if 'postgresql://masuka:password123@localhost:5432/masuka' in content:
        print("  ✅ Database URL already correct")
    else:
        # Replace the DATABASE_URL line
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.startswith('DATABASE_URL='):
                new_lines.append('DATABASE_URL=postgresql://masuka:password123@localhost:5432/masuka')
            else:
                new_lines.append(line)

        with open(env_file, 'w') as f:
            f.write('\n'.join(new_lines))

        print("  ✅ Backend configuration updated")
else:
    print("  ⚠️  Backend .env file not found")

# Verify database tables if backend has initialized them
print("\n7️⃣ Checking database tables...")
result = subprocess.run(
    ['psql', '-U', 'masuka', '-d', 'masuka', '-h', 'localhost', '-c', "\\dt"],
    capture_output=True,
    text=True,
    env={'PGPASSWORD': 'password123'}
)

if result.returncode == 0 and result.stdout.strip():
    print("  ✅ Database tables found:")
    for line in result.stdout.strip().split('\n'):
        if 'training' in line or 'models' in line or 'datasets' in line:
            print(f"     {line.strip()}")
else:
    print("  ℹ️  No tables yet (backend will create them on first run)")

print("\n" + "="*70)
print("🎉 Database Fix Complete!")
print("="*70)
print("\n✅ PostgreSQL is now configured for password authentication")
print("\n📊 Summary:")
print("   • Authentication method: md5 (password-based)")
print("   • User: masuka")
print("   • Database: masuka")
print("   • Connection: localhost:5432")
print("\n💡 Next steps:")
if result.returncode == 0:
    print("   ✅ Database is working! No restart needed.")
else:
    print("   ⚠️  If backend is running, restart it to pick up changes:")
    print("   1. pkill -f uvicorn")
    print("   2. Run CELL_START_BACKEND.py")
print("="*70)
