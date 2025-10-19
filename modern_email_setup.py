# Modern Email Setup - SendGrid Integration
from flask import Flask, request, jsonify
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import os

# SendGrid configuration
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', 'your-sendgrid-api-key')
FROM_EMAIL = 'noreply@yigal-sofer-law.com'  # Your domain email
TO_EMAIL = 'galsofer6@gmail.com'

def send_email_sendgrid(form_data):
    """
    Send email using SendGrid (modern way)
    """
    try:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        
        # Create email content
        subject = f'בקשה חדשה מאתר המשרד - {form_data["service"]}'
        
        html_content = f"""
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; direction: rtl; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f8f9fa; padding: 20px; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #2c3e50; }}
                .value {{ margin-top: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>בקשה חדשה מאתר המשרד</h2>
                </div>
                <div class="content">
                    <div class="field">
                        <div class="label">שם:</div>
                        <div class="value">{form_data['name']}</div>
                    </div>
                    <div class="field">
                        <div class="label">טלפון:</div>
                        <div class="value">{form_data['phone']}</div>
                    </div>
                    <div class="field">
                        <div class="label">אימייל:</div>
                        <div class="value">{form_data['email']}</div>
                    </div>
                    <div class="field">
                        <div class="label">תחום שירות:</div>
                        <div class="value">{form_data['service']}</div>
                    </div>
                    <div class="field">
                        <div class="label">הודעה:</div>
                        <div class="value">{form_data['message']}</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create mail object
        from_email = Email(FROM_EMAIL, "משרד עו\"ד יגאל סופר")
        to_email = To(TO_EMAIL)
        content = Content("text/html", html_content)
        
        mail = Mail(from_email, to_email, subject, content)
        
        # Send email
        response = sg.send(mail)
        
        if response.status_code == 202:
            return True
        else:
            print(f"SendGrid Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"SendGrid Exception: {str(e)}")
        return False

# Alternative: EmailJS (JavaScript solution)
EMAILJS_TEMPLATE = """
// EmailJS Configuration (JavaScript)
(function() {
    emailjs.init("YOUR_USER_ID"); // Replace with your EmailJS user ID
    
    window.sendEmail = function(formData) {
        const templateParams = {
            name: formData.name,
            phone: formData.phone,
            email: formData.email,
            service: formData.service,
            message: formData.message,
            to_email: 'galsofer6@gmail.com'
        };
        
        return emailjs.send('YOUR_SERVICE_ID', 'YOUR_TEMPLATE_ID', templateParams);
    };
})();
"""
