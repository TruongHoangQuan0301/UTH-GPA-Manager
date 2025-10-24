# UTH GPA Manager

A web application for University of Transport HCMC (UTH) students to manage and calculate their GPA.

## Features

- Student account management with UTH email verification
- Secure authentication system
- Password reset functionality with email confirmation
- GPA calculation for each semester
- Overall GPA tracking
- Subject management
- Mobile-friendly interface

## Technology Stack

- Python/Flask for backend
- SQLite for database
- Bootstrap for frontend
- Flask-Login for authentication
- HTML/CSS/JavaScript for user interface

## Installation

1. Clone the repository:
```bash
git clone https://github.com/TruongHoangQuan0301/UTH-GPA-Manager.git
cd UTH-GPA-Manager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
python app.py
```

4. Configure email settings:
Edit `utils/email_utils.py` and set your email credentials for password reset functionality.

## Usage

1. Run the application:
```bash
python app.py
```

2. Open a web browser and navigate to:
```
http://localhost:5000
```

## Security Features

- Password hashing using werkzeug.security
- Token-based password reset
- UTH student email validation
- Session management
- CSRF protection

## Contributing

Feel free to submit issues and enhancement requests.

## License

[MIT License](LICENSE)

## Contact

For support or queries, contact the IT Department:
- Phone: (028) 3512 0784
- Email: it@ut.edu.vn