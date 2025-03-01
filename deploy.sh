ECHO is on.
#!/bin/bash
# deploy.sh

echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations
echo "Running migrations..."
python manage.py migrate


# Optionally create a superuser (uncomment if needed)
# echo "Creating superuser..."
#    python manage.py createsuperuser --noinput --username $SUPERUSER_USERNAME --email $SUPERUSER_EMAIL  --user_type admin