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
if python manage.py shell -c "from accounts.models import User; print(User.objects.filter(username='$SUPERUSER_USERNAME').exists())" | grep -q "True"; then
    echo "Superuser already exists. Skipping superuser creation."
else
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput --username $SUPERUSER_USERNAME --email $SUPERUSER_EMAIL --user_type admin
fi


# Check if manager exists before creating
echo "Checking if manager exists..."
if python manage.py shell -c "from accounts.models import User; print(User.objects.filter(email='manager@gmail.com').exists())" | grep -q "True"; then
    echo "Manager already exists. Skipping manager creation."
else
    echo "Creating manager..."
    python manage.py shell -c "from accounts.models import User; User.objects.create_user(username='manager', email='manager@gmail.com', password='Manager@1234', user_type='manager')"
fi

