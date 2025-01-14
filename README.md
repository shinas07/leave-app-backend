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

### Authentication
- `POST /api/token/` - Get JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Leave Management
- `GET /api/leave-history/` - List all leaves
- `POST /api/apply-leave/` - Create leave request
- `GET /api/dashboard/datas/` - Get dashboard details
- `DELETE /api/leaves/<id>/` - Delete leave request

### User Management
- `GET /api/employees/` - List all users
- `GET /api/leave/all-requests` - Get all leave requests

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

📝 Conclusion
This backend system provides a robust solution for managing leave applications, approval workflows, and user authentication. For more details or to contribute, feel free to open an issue or submit a pull request.

📞 Contact
For questions or support, please reach out to [shinasaman07@gmail.com]