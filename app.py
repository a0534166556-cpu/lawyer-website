from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session
from flask_wtf import FlaskForm
from wtforms import StringField, TelField, EmailField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import sendgrid
from sendgrid.helpers.mail import Mail, Email as SendGridEmail, To, Content
from config import config
from facebook_integration import get_facebook_posts
import mysql.connector
from mysql.connector import Error
import uuid

app = Flask(__name__)
config_name = os.environ.get('FLASK_ENV') or 'default'
app.config.from_object(config[config_name])

# מסד נתונים להודעות - MySQL
def get_db_connection():
    """יצירת חיבור למסד הנתונים MySQL"""
    print(f"🔗 מנסה להתחבר למסד הנתונים:")
    print(f"   Host: {app.config['MYSQL_HOST']}")
    print(f"   Port: {app.config['MYSQL_PORT']}")
    print(f"   User: {app.config['MYSQL_USER']}")
    print(f"   Database: {app.config['MYSQL_DATABASE']}")
    
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            port=app.config['MYSQL_PORT'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DATABASE']
        )
        print("✅ חיבור למסד הנתונים הצליח!")
        return connection
    except Error as e:
        print(f"❌ שגיאה בחיבור למסד הנתונים: {e}")
        return None

def init_db():
    """יצירת טבלת הודעות"""
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to database")
        return
    
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lawyer_messages (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            email VARCHAR(100) NOT NULL,
            service VARCHAR(100) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'unread'
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialized successfully!")

def save_message(form_data):
    """שמירת הודעה במסד הנתונים"""
    print(f"🔍 מנסה לשמור הודעה: {form_data['name']}")
    
    conn = get_db_connection()
    if conn is None:
        print("❌ לא הצליח להתחבר למסד הנתונים")
        return None
    
    print("✅ התחבר למסד הנתונים בהצלחה")
    
    cursor = conn.cursor()
    message_id = str(uuid.uuid4())
    
    try:
        cursor.execute('''
            INSERT INTO lawyer_messages (id, name, phone, email, service, message)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (message_id, form_data['name'], form_data['phone'], 
              form_data['email'], form_data['service'], form_data['message']))
        
        conn.commit()
        print(f"✅ הודעה נשמרה בהצלחה עם ID: {message_id}")
        
    except Exception as e:
        print(f"❌ שגיאה בשמירת הודעה: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
    
    return message_id

def get_all_messages():
    """קבלת כל ההודעות"""
    conn = get_db_connection()
    if conn is None:
        return []
    
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM lawyer_messages ORDER BY created_at DESC')
    messages = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # המרה לרשימת מילונים
    message_list = []
    for msg in messages:
        message_list.append({
            'id': msg[0],
            'name': msg[1],
            'phone': msg[2],
            'email': msg[3],
            'service': msg[4],
            'message': msg[5],
            'created_at': msg[6],
            'status': msg[7]
        })
    
    return message_list

def mark_message_as_read(message_id):
    """סימון הודעה כנקראה"""
    conn = get_db_connection()
    if conn is None:
        return
    
    cursor = conn.cursor()
    cursor.execute('UPDATE lawyer_messages SET status = %s WHERE id = %s', ('read', message_id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_message(message_id):
    """מחיקת הודעה"""
    conn = get_db_connection()
    if conn is None:
        return
    
    cursor = conn.cursor()
    cursor.execute('DELETE FROM lawyer_messages WHERE id = %s', (message_id,))
    conn.commit()
    cursor.close()
    conn.close()

# יצירת מסד הנתונים בהפעלה
init_db()

# סיסמה לפאנל מנהל
ADMIN_PASSWORD = "13300"

def admin_required(f):
    """דקורטור לבדיקת הרשאות מנהל"""
    def decorated_function(*args, **kwargs):
        # בדיקה חזקה מאוד
        admin_logged_in = session.get('admin_logged_in', False)
        admin_password_correct = session.get('admin_password_correct', False)
        
        if not admin_logged_in or not admin_password_correct:
            session.clear()
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

class ContactForm(FlaskForm):
    name = StringField('שם מלא', validators=[
        DataRequired(message='שם מלא הוא שדה חובה'),
        Length(min=2, max=50, message='השם חייב להיות בין 2 ל-50 תווים')
    ])
    phone = TelField('טלפון', validators=[
        DataRequired(message='מספר טלפון הוא שדה חובה')
    ])
    email = EmailField('אימייל', validators=[
        DataRequired(message='כתובת אימייל היא שדה חובה'),
        Email(message='כתובת אימייל לא תקינה')
    ])
    service = SelectField('תחום שירות', 
                         choices=[
                             ('', 'בחר תחום שירות'),
                             ('torts', 'נזיקין'),
                             ('personal-injury', 'נזקי גוף'),
                             ('road-accidents', 'תאונות דרכים'),
                             ('national-insurance', 'ביטוח לאומי'),
                             ('real-estate', 'מקרקעין'),
                             ('labor', 'דיני עבודה'),
                             ('notary', 'שירותי נוטריון'),
                             ('prenup', 'הסכמי ממון')
                         ],
                         validators=[DataRequired(message='יש לבחור תחום שירות')])
    message = TextAreaField('תיאור המקרה', validators=[
        DataRequired(message='תיאור המקרה הוא שדה חובה'),
        Length(min=10, max=500, message='התיאור חייב להיות בין 10 ל-500 תווים')
    ])
    submit = SubmitField('שלח בקשה')

class AdminLoginForm(FlaskForm):
    password = StringField('סיסמת מנהל', validators=[
        DataRequired(message='נדרשת סיסמה'),
        Length(min=1, max=20, message='סיסמה לא תקינה')
    ])
    submit = SubmitField('התחבר')

class QuickContactForm(FlaskForm):
    name = StringField('שם מלא', validators=[
        DataRequired(message='שם מלא הוא שדה חובה'),
        Length(min=2, max=50, message='השם חייב להיות בין 2 ל-50 תווים')
    ])
    phone = TelField('טלפון', validators=[
        DataRequired(message='מספר טלפון הוא שדה חובה')
    ])
    email = EmailField('אימייל', validators=[
        DataRequired(message='כתובת אימייל היא שדה חובה'),
        Email(message='כתובת אימייל לא תקינה')
    ])
    service = SelectField('תחום שירות', 
                         choices=[
                             ('', 'בחר תחום שירות'),
                             ('torts', 'נזיקין'),
                             ('personal-injury', 'נזקי גוף'),
                             ('road-accidents', 'תאונות דרכים'),
                             ('national-insurance', 'ביטוח לאומי'),
                             ('real-estate', 'מקרקעין'),
                             ('labor', 'דיני עבודה'),
                             ('notary', 'שירותי נוטריון'),
                             ('prenup', 'הסכמי ממון')
                         ],
                         validators=[DataRequired(message='יש לבחור תחום שירות')])
    message = TextAreaField('תיאור המקרה', validators=[
        DataRequired(message='תיאור המקרה הוא שדה חובה'),
        Length(min=10, max=500, message='התיאור חייב להיות בין 10 ל-500 תווים')
    ])
    submit = SubmitField('שלח בקשה')

def send_email(form_data):
    """Send email notification using SendGrid"""
    try:
        sg = sendgrid.SendGridAPIClient(api_key=app.config['SENDGRID_API_KEY'])
        
        # Create email content with beautiful HTML
        subject = f'בקשה חדשה מאתר המשרד - {form_data["service"]}'
        
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    direction: rtl; 
                    margin: 0; 
                    padding: 0; 
                    background-color: #f8f9fa;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 20px auto; 
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }}
                .header {{ 
                    background: linear-gradient(135deg, #2c3e50, #3498db);
                    color: white; 
                    padding: 30px; 
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                    font-weight: 600;
                }}
                .content {{ 
                    padding: 30px;
                }}
                .field {{ 
                    margin-bottom: 20px;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 8px;
                    border-right: 4px solid #3498db;
                }}
                .label {{ 
                    font-weight: bold; 
                    color: #2c3e50; 
                    font-size: 14px;
                    margin-bottom: 5px;
                    display: block;
                }}
                .value {{ 
                    color: #34495e;
                    font-size: 16px;
                }}
                .message-field {{
                    background: #ecf0f1;
                    border-right-color: #e74c3c;
                }}
                .footer {{
                    background: #34495e;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📧 בקשה חדשה מאתר המשרד</h1>
                    <p>משרד עו"ד ונוטריון יגאל סופר</p>
                </div>
                <div class="content">
                    <div class="field">
                        <span class="label">👤 שם מלא:</span>
                        <div class="value">{form_data['name']}</div>
                    </div>
                    <div class="field">
                        <span class="label">📞 טלפון:</span>
                        <div class="value">{form_data['phone']}</div>
                    </div>
                    <div class="field">
                        <span class="label">📧 אימייל:</span>
                        <div class="value">{form_data['email']}</div>
                    </div>
                    <div class="field">
                        <span class="label">⚖️ תחום שירות:</span>
                        <div class="value">{form_data['service']}</div>
                    </div>
                    <div class="field message-field">
                        <span class="label">💬 הודעה:</span>
                        <div class="value">{form_data['message']}</div>
                    </div>
                </div>
                <div class="footer">
                    <p>תאריך: {datetime.now().strftime('%d/%m/%Y %H:%M')} | משרד עו"ד ונוטריון יגאל סופר</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create mail object
        from_email = SendGridEmail(app.config['FROM_EMAIL'], "משרד עו\"ד יגאל סופר")
        to_email = To(app.config['RECIPIENT_EMAIL'])
        content = Content("text/html", html_content)
        
        mail = Mail(from_email, to_email, subject, content)
        
        # Send email
        response = sg.send(mail)
        
        if response.status_code == 202:
            print("Email sent successfully via SendGrid")
            return True
        else:
            print(f"SendGrid Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"SendGrid Exception: {str(e)}")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ContactForm()
    quick_form = QuickContactForm()
    
    # Handle quick contact form from homepage
    if quick_form.validate_on_submit():
        form_data = {
            'name': quick_form.name.data,
            'phone': quick_form.phone.data,
            'email': quick_form.email.data,
            'service': dict(quick_form.service.choices)[quick_form.service.data],
            'message': quick_form.message.data
        }
        
        # Save message to database
        save_message(form_data)
        
        # הודעה נשמרה בהצלחה
        flash('תודה על פנייתך! נחזור אליך בהקדם האפשרי.', 'success')
        
        return redirect(url_for('index'))
    
    return render_template('index.html', form=form, quick_form=quick_form)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    quick_form = QuickContactForm()
    
    print(f"🔍 Contact route called - Method: {request.method}")
    
    # Handle regular contact form
    if form.validate_on_submit():
        print("✅ Form validation passed!")
        form_data = {
            'name': form.name.data,
            'phone': form.phone.data,
            'email': form.email.data,
            'service': dict(form.service.choices)[form.service.data],
            'message': form.message.data
        }
        
        print(f"📝 Form data: {form_data}")
        
        # Save message to database
        save_message(form_data)
        
        # הודעה נשמרה בהצלחה
        flash('תודה על פנייתך! נחזור אליך בהקדם האפשרי.', 'success')
        
        return redirect(url_for('contact'))
    else:
        print("❌ Form validation failed!")
        if request.method == 'POST':
            print(f"Form errors: {form.errors}")
    
    # Handle quick contact form
    if quick_form.validate_on_submit():
        form_data = {
            'name': quick_form.name.data,
            'phone': quick_form.phone.data,
            'email': quick_form.email.data,
            'service': dict(quick_form.service.choices)[quick_form.service.data],
            'message': quick_form.message.data
        }
        
        # Save message to database
        save_message(form_data)
        
        # הודעה נשמרה בהצלחה
        flash('תודה על פנייתך! נחזור אליך בהקדם האפשרי.', 'success')
        
        return redirect(url_for('contact'))
    
    return render_template('contact.html', form=form, quick_form=quick_form)

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """דף התחברות לפאנל מנהל"""
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        if form.password.data == ADMIN_PASSWORD:
            # שומר שני סימנים לוודא שהמשתמש באמת התחבר
            session['admin_logged_in'] = True
            session['admin_password_correct'] = True
            session['admin_login_time'] = datetime.now().timestamp()
            flash('התחברת בהצלחה לפאנל המנהל', 'success')
            return redirect(url_for('admin'))
        else:
            flash('סיסמה שגויה', 'error')
    
    return render_template('admin_login.html', form=form)

@app.route('/admin/logout')
def admin_logout():
    """התנתקות מפאנל המנהל"""
    session.clear()  # מנקה את כל ה-session
    flash('התנתקת מפאנל המנהל', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/clear-session')
def clear_admin_session():
    """ניקוי session - לבדיקות"""
    session.clear()
    return "Session cleared! Now try /admin again"

@app.route('/force-logout')
def force_logout():
    """כפיית התנתקות - מנקה הכל"""
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/reset-admin')
def reset_admin():
    """איפוס מלא של פאנל המנהל"""
    session.clear()
    return """
    <html dir="rtl">
    <head><title>איפוס פאנל מנהל</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>פאנל המנהל אופס בהצלחה!</h1>
        <p>כל ה-session נמחק. עכשיו תוכל להתחבר מחדש.</p>
        <a href="/admin/login" style="background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">התחבר לפאנל מנהל</a>
    </body>
    </html>
    """

@app.route('/admin')
def admin():
    """פאנל מנהל - הצגת כל ההודעות"""
    # בדיקה חזקה מאוד - תמיד בודק אם מחובר
    admin_logged_in = session.get('admin_logged_in', False)
    admin_password_correct = session.get('admin_password_correct', False)
    
    # אם לא מחובר - מנקה הכל ומעביר להתחברות
    if not admin_logged_in or not admin_password_correct:
        session.clear()
        flash('נדרשת הרשאת מנהל', 'error')
        return redirect(url_for('admin_login'))
    
    messages = get_all_messages()
    return render_template('admin.html', messages=messages)

@app.route('/admin/mark-read/<message_id>', methods=['POST'])
@admin_required
def admin_mark_read(message_id):
    """סימון הודעה כנקראה"""
    try:
        mark_message_as_read(message_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/delete/<message_id>', methods=['DELETE'])
@admin_required
def admin_delete(message_id):
    """מחיקת הודעה"""
    try:
        delete_message(message_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/call/<message_id>')
@admin_required
def admin_call(message_id):
    """התקשרות ללקוח"""
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'error': 'Database connection failed'})
        
        cursor = conn.cursor()
        cursor.execute('SELECT name, phone FROM lawyer_messages WHERE id = %s', (message_id,))
        result = cursor.fetchone()
        
        if result:
            name, phone = result
            # יצירת קישור לטלפון
            phone_link = f"tel:{phone}"
            return jsonify({'success': True, 'phone_link': phone_link, 'name': name, 'phone': phone})
        else:
            return jsonify({'success': False, 'error': 'Message not found'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

@app.route('/admin/email/<message_id>')
@admin_required
def admin_email(message_id):
    """שליחת אימייל ללקוח"""
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'error': 'Database connection failed'})
        
        cursor = conn.cursor()
        cursor.execute('SELECT name, email FROM lawyer_messages WHERE id = %s', (message_id,))
        result = cursor.fetchone()
        
        if result:
            name, email = result
            # יצירת קישור לאימייל
            email_link = f"mailto:{email}?subject=תשובה לבקשתך - משרד עו\"ד ונוטריון יגאל סופר&body=שלום {name},\n\nתודה על פנייתך אלינו.\n\nבברכה,\nמשרד עו\"ד ונוטריון יגאל סופר"
            return jsonify({'success': True, 'email_link': email_link, 'name': name, 'email': email})
        else:
            return jsonify({'success': False, 'error': 'Message not found'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

@app.route('/all-articles')
def all_articles():
    # נסה להביא מאמרים מהפייסבוק
    facebook_posts = get_facebook_posts()
    
    # אם יש פוסטים מהפייסבוק, נשתמש בהם
    if facebook_posts:
        return render_template('all_articles.html', facebook_posts=facebook_posts)
    else:
        # אחרת נשתמש במאמרים הסטטיים
        return render_template('all_articles.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.route('/blog/<int:post_id>')
def blog_post(post_id):
    """Display individual blog post"""
    posts = {
        1: {
            'title': 'נזיקין תביעות',
            'author': 'יגאל סופר עורך דין ונוטריון',
            'date': '15/01/2025 14:30',
            'image': 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=400&h=250&fit=crop',
            'content': '''
            <h2>נזיקין תביעות - המדריך המלא</h2>
            <p>תביעות נזיקין הן תביעות אזרחיות שמטרתן לקבל פיצוי בגין נזק שנגרם לאדם או לרכושו כתוצאה מפעולה או מחדל של אחר.</p>
            
            <h3>סוגי תביעות נזיקין:</h3>
            <ul>
                <li><strong>תאונות דרכים</strong> - פיצוי בגין נזקי גוף ורכוש</li>
                <li><strong>תאונות עבודה</strong> - פיצוי מול ביטוח לאומי</li>
                <li><strong>רשלנות רפואית</strong> - פיצוי בגין טיפול רפואי רשלני</li>
                <li><strong>נזקי רכוש</strong> - פיצוי בגין נזק לרכוש</li>
            </ul>
            
            <h3>מה צריך להוכיח בתביעת נזיקין?</h3>
            <p>על התובע להוכיח שלושה יסודות עיקריים:</p>
            <ol>
                <li><strong>נזק</strong> - נזק ממשי שנגרם לתובע</li>
                <li><strong>קשר סיבתי</strong> - קשר בין הפעולה לנזק</li>
                <li><strong>אשמה</strong> - רשלנות או כוונה של הנתבע</li>
            </ol>
            
            <p>אם נפגעתם ונזקקתם לשירות משפטי מקצועי, פנו אלינו לקבלת ייעוץ מקצועי.</p>
            '''
        },
        2: {
            'title': 'תאונת עבודה מול הביטוח הלאומי',
            'author': 'יגאל סופר עורך דין ונוטריון',
            'date': '22/01/2025 11:15',
            'image': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=400&h=250&fit=crop',
            'content': '''
            <h2>תאונת עבודה - זכויותיכם מול הביטוח הלאומי</h2>
            <p>תאונת עבודה מוגדרת כתאונה שאירעה תוך כדי עבודה ובעקבות העבודה, והיא מזכה בפיצויים מהביטוח הלאומי.</p>
            
            <h3>מה נחשב כתאונת עבודה?</h3>
            <ul>
                <li>תאונה במקום העבודה</li>
                <li>תאונה בדרך לעבודה או חזרה ממנה</li>
                <li>תאונה במהלך פעילות מטעם העבודה</li>
                <li>מחלת מקצוע</li>
            </ul>
            
            <h3>הזכויות שלכם:</h3>
            <ol>
                <li><strong>דמי פגיעה</strong> - תשלום יומי בגין ימי העדרות מהעבודה</li>
                <li><strong>פיצוי חד פעמי</strong> - בגין נכות שנגרמה</li>
                <li><strong>גמלת נכות כללית</strong> - במקרה של נכות קבועה</li>
                <li><strong>שיקום מקצועי</strong> - במקרה הצורך</li>
            </ol>
            
            <h3>חשוב לדעת:</h3>
            <p>יש לדווח על התאונה לביטוח הלאומי תוך 12 חודשים מיום התאונה. במידה והביטוח הלאומי דוחה את התביעה, ניתן לערער על ההחלטה.</p>
            
            <p>לסיוע משפטי בתביעות תאונות עבודה, פנו אלינו לקבלת ייעוץ מקצועי.</p>
            '''
        },
        3: {
            'title': 'תאונות עם מעורבות של אופניים חשמליים',
            'author': 'יגאל סופר עורך דין ונוטריון',
            'date': '28/01/2025 16:45',
            'image': 'https://images.unsplash.com/photo-1581578731548-c7e3d1c1c9d9?w=400&h=250&fit=crop',
            'content': '''
            <h2>תאונות אופניים חשמליים - המדריך המשפטי</h2>
            <p>עם העלייה בשימוש באופניים חשמליים, חלה עלייה משמעותית במספר התאונות. חשוב להכיר את הזכויות והחובות במקרה של תאונה.</p>
            
            <h3>החוק לגבי אופניים חשמליים:</h3>
            <ul>
                <li>גיל מינימלי: 16 שנים</li>
                <li>חובת חבישת קסדה עד גיל 18</li>
                <li>מהירות מקסימלית: 25 קמ"ש</li>
                <li>חובת ביטוח חובה (מרץ 2024)</li>
            </ul>
            
            <h3>במקרה של תאונה:</h3>
            <ol>
                <li><strong>זכרו את הפרטים</strong> - רשום מספרי רכבים, פרטי עדים</li>
                <li><strong>הזמינו משטרה</strong> - במיוחד אם יש נזקי גוף</li>
                <li><strong>צלמו את המקום</strong> - תמונות מהתאונה</li>
                <li><strong>פנו לטיפול רפואי</strong> - גם אם הנזק נראה קל</li>
                <li><strong>שמרו על המסמכים</strong> - קבלות, הפניות רפואיות</li>
            </ol>
            
            <h3>הפיצויים המגיעים:</h3>
            <p>אם נפגעתם בתאונת אופניים חשמליים, ייתכן שמגיעים לכם פיצויים עבור:</p>
            <ul>
                <li>נזקי גוף</li>
                <li>נזקי רכוש</li>
                <li>אובדן כושר השתכרות</li>
                <li>הוצאות רפואיות</li>
                <li>כאב וסבל</li>
            </ul>
            
            <p>לסיוע משפטי בתביעות תאונות אופניים, פנו אלינו לקבלת ייעוץ מקצועי.</p>
            '''
        }
    }
    
    post = posts.get(post_id)
    if not post:
        return "מאמר לא נמצא", 404
    
    return render_template('blog_post.html', post=post)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
