# Leave Application System Backend

Django Rest Framework backend for the Leave Application and Approval System. This API handles leave management, user authentication, and leave approval workflows.

## 🛠️ Tech Stack

- Django Rest Framework
- PostgreSQL Database
- JWT Authentication
- Python 3.x

## ⚙️ Environment Setup

1. Create a `.env` file in the root directory with the following variables:
```env
DB_NAME=leave_management_db_mmkg
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=5432
```

## 📁 Project Structure
```
backend/
├── accounts/           # User authentication app
├── leave_manager/      # Leave management app
├── leave_app/         # Main project settings
├── manage.py         
├── requirements.txt   
└── staticfiles/      
```

## 🚀 Local Development

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Start development server:
```bash
python manage.py runserver
```

## 📌 API Endpoints

### Authentication (`/auth/`)
- `POST /auth/login/` - User login
- `POST /auth/logout/` - User logout
- `POST /auth/refresh/` - Refresh JWT token
- `GET /auth/user/` - Get user details
- `POST /auth/register-manager/` - Register new manager

### Leave Management (`/api/`)
- `POST /api/apply-leave/` - Submit leave application
- `PUT /api/approve-leave/<int:pk>/` - Approve specific leave request
- `GET /api/leave-history/` - View leave history
- `GET /api/dashboard/datas/` - Get dashboard data
- `GET /api/leave/requests/` - Get leave requests
- `POST /api/leave/approve/` - Approve leave request
- `POST /api/leave/reject/` - Reject leave request
- `GET /api/leave/all-requests/` - View all leave requests

### Employee Management (`/api/`)
- `GET /api/employees/` - List all employees
- `POST /api/employees/create/` - Create new employee
- `GET /api/dashboard/stats/` - Get dashboard statistics
- `GET /api/dashboard/requests/` - Get dashboard requests

### System Health
- `GET /health/` - Health check endpoint
- `GET /` - Home view
- `GET /admin/` - Admin interface

## 🌐 Deployment (Render)

1. Create a new Web Service on Render
2. Link to your GitHub repository
3. Configure environment variables in Render dashboard
4. Set build command:
```bash
pip install -r requirements.txt
```
5. Set start command:
```bash
gunicorn leave_app.wsgi:application
```

## 🔐 Security Notes

- Keep `.env` file secure and never commit to repository
- Use strong passwords for database credentials
- Regularly update dependencies for security patches
- Configure CORS settings appropriately in `settings.py`

## 🐛 Troubleshooting

Common issues and solutions:

1. Database connection errors:
   - Verify database credentials in `.env`
   - Check if database server is running
   - Ensure proper network access

2. Migration issues:
   - Run `python manage.py makemigrations`
   - Then `python manage.py migrate`

3. Static files not serving:
   - Run `python manage.py collectstatic`
   - Check `STATIC_ROOT` in settings

## 📝 Conclusion
This backend system provides a robust solution for managing leave applications, approval workflows, and user authentication. For more details or to contribute, feel free to open an issue or submit a pull request.

## 📞 Contact
For questions or support, please reach out to [shinasaman07@gmail.com]