"""
Utilities for handling email verification and password reset.
"""
import re
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from datetime import datetime, timedelta

def validate_student_email(email):
    """
    Validate UTH student email format.
    Format: [name without accents][last 4 digits of CCCD]@ut.edu.vn
    """
    pattern = r'^[a-zA-Z0-9]+\d{4}@ut\.edu\.vn$'
    return bool(re.match(pattern, email))

def generate_reset_token():
    """Generate a random token for password reset."""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(32))

def send_reset_email(email, username, reset_link):
    """
    Send password reset email to student.
    
    Args:
        email (str): Student's email address
        username (str): Student's username
        reset_link (str): Complete password reset URL
    """
    # Email configuration
    sender_email = "your-email@gmail.com"  # Replace with your email
    sender_password = "your-app-password"   # Replace with your app password

    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "UTH GPA Manager - Đặt lại mật khẩu"

    # Email content with HTML formatting
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2 style="color: #004d40;">UTH GPA Manager Pro - Đặt lại mật khẩu</h2>
        <p>Xin chào {username},</p>
        <p>Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản GPA Manager.</p>
        <p>Vui lòng click vào link bên dưới để đặt lại mật khẩu:</p>
        <p>
            <a href="{reset_link}" 
               style="background-color: #004d40; 
                      color: white; 
                      padding: 10px 20px; 
                      text-decoration: none; 
                      border-radius: 5px;">
                Đặt lại mật khẩu
            </a>
        </p>
        <p>Link này sẽ hết hạn sau 24 giờ.</p>
        <p>Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.</p>
        <hr>
        <p style="color: #666; font-size: 12px;">
            Email này được gửi tự động từ hệ thống UTH GPA Manager Pro.<br>
            Vui lòng không trả lời email này.
        </p>
    </body>
    </html>
    """

    msg.attach(MIMEText(body, 'html'))

    try:
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send email
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False