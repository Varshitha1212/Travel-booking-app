# Travel Booking Application

A Django-based travel booking web application that allows users to view available travel options, book tickets, and manage their bookings.

## Features

### ✅ Completed Features

1. **User Management**
   - User registration, login, and logout
   - Profile management with extended user information
   - Django's built-in authentication system

2. **Travel Options**
   - Complete TravelOption model with all required fields
   - Support for Flight, Train, and Bus options
   - Source, destination, departure time, price, and seat availability

3. **Booking System**
   - Book travel options with seat selection
   - Booking model with all required fields
   - Automatic price calculation
   - Seat availability validation

4. **Booking Management**
   - View current and past bookings
   - Cancel bookings with automatic seat restoration
   - Booking status tracking (Confirmed/Cancelled)

5. **Frontend**
   - Modern, responsive UI using Bootstrap
   - Beautiful gradient design with modern styling
   - Search and filtering capabilities
   - Mobile-responsive design
   - Auto-complete for cities

6. **Admin Interface**
   - Django admin interface for managing travel options
   - Admin panels for bookings and user profiles

7. **Testing & Validation**
   - Comprehensive unit tests (14 tests passing)
   - Form validation for seat availability
   - Input validation and error handling
   - Sample data management command

8. **Bonus Features**
   - MySQL database support
   - Advanced filtering and search
   - Responsive design for all devices
   - Auto-complete for city inputs

## Requirements

- Python 3.8+
- Django 5.2.5
- python-dotenv
- mysqlclient (for MySQL support)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Varshitha1212/Travel-booking-app.git
cd Travel-booking-app
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory:
```
DB_ENGINE=sqlite  # or mysql for MySQL
SECRET_KEY=your-secret-key
DEBUG=True

# For MySQL (optional):
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Load sample data (optional):
```bash
python manage.py load_sample_data
```

8. Run the development server:
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## Database Configuration

The application supports both SQLite (default) and MySQL databases:

- **SQLite**: Set `DB_ENGINE=sqlite` in `.env` file
- **MySQL**: Set `DB_ENGINE=mysql` and provide MySQL credentials

## Project Structure

```
Travel-booking-app/
├── bookings/                 # Main Django app
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── forms.py             # Django forms
│   ├── urls.py              # URL patterns
│   ├── admin.py             # Admin interface
│   └── templates/           # HTML templates
├── templates/               # Base templates
├── static/                  # Static files (CSS, JS)
├── travelbooker/           # Django project settings
├── requirements.txt        # Python dependencies
├── manage.py              # Django management script
└── README.md              # This file
```

## Usage

1. **Register/Login**: Create an account or login with existing credentials
2. **Browse Options**: View available travel options with filtering
3. **Book Travel**: Select options and book tickets
4. **Manage Bookings**: View and cancel bookings from your profile
5. **Admin Panel**: Access `/admin/` to manage travel options and bookings

## API Endpoints

- `/` - Home page with travel options
- `/book/<id>/` - Book a specific travel option
- `/my-bookings/` - View user bookings
- `/cancel/<id>/` - Cancel a booking
- `/profile/` - User profile management
- `/accounts/login/` - User login
- `/signup/` - User registration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is created for educational purposes.

## Deployment

### Quick Deployment to PythonAnywhere (Recommended)

1. **Sign up** at [PythonAnywhere.com](https://www.pythonanywhere.com)
2. **Upload your code** to PythonAnywhere
3. **Set up virtual environment** and install requirements
4. **Configure MySQL database** (free tier available)
5. **Set environment variables** in `.env` file
6. **Run migrations** and create superuser
7. **Load sample data**: `python manage.py load_sample_data`
8. **Configure WSGI file** to point to your Django app
9. **Collect static files**: `python manage.py collectstatic`

### AWS EC2 Deployment

1. **Launch EC2 instance** (Ubuntu recommended)
2. **Install dependencies**: Python, nginx, MySQL
3. **Clone repository** and set up virtual environment
4. **Configure MySQL database**
5. **Set up Gunicorn** as WSGI server
6. **Configure Nginx** as reverse proxy
7. **Set up SSL** with Let's Encrypt

### Environment Variables for Production

Create a `.env` file with:
```
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com,your-ip-address
DB_ENGINE=mysql
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=3306
```

### Pre-deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up production database
- [ ] Run `python manage.py check --deploy`
- [ ] Test all features locally
- [ ] Update `SECRET_KEY`
- [ ] Configure static files
- [ ] Set up SSL certificate

## Testing

Run the test suite:
```bash
python manage.py test bookings.tests
```

All 14 tests should pass, covering:
- User registration and authentication
- Travel option creation and filtering
- Booking creation and cancellation
- Form validation
- Profile management
