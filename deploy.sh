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

# Check if superuser exists before creating
echo "Checking if superuser exists..."
if python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='$SUPERUSER_USERNAME').exists())" | grep -q "True"; then
    echo "Superuser already exists. Skipping superuser creation."
else
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput --username $SUPERUSER_USERNAME --email $SUPERUSER_EMAIL --user_type admin
fi


