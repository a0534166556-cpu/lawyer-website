import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MySQL Database configuration
    # Railway will provide these via environment variables
    MYSQL_HOST = os.environ.get('MYSQLHOST') or os.environ.get('MYSQL_HOST') or 'hopper.proxy.rlwy.net'
    MYSQL_PORT = int(os.environ.get('MYSQLPORT') or os.environ.get('MYSQL_PORT') or 14589)
    MYSQL_USER = os.environ.get('MYSQLUSER') or os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQLPASSWORD') or os.environ.get('MYSQL_PASSWORD') or 'BsvRVNeGHqRRADmspwHGWGcgabUhVPtw'
    MYSQL_DATABASE = os.environ.get('MYSQLDATABASE') or os.environ.get('MYSQL_DATABASE') or 'railway'
    
    # Email configuration - SendGrid
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY') or 'your-sendgrid-api-key-here'
    FROM_EMAIL = os.environ.get('FROM_EMAIL') or 'galsofer6@gmail.com'
    RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL') or 'galsofer6@gmail.com'  # ניתן לשנות כאן
    EMAIL_ENABLED = os.environ.get('EMAIL_ENABLED', 'true').lower() == 'true'  # אפשרות להשבית אימיילים
    
    # Office information
    OFFICE_NAME = "משרד עו\"ד ונוטריון יגאל סופר"
    OFFICE_PHONE = "08-993-1666"
    OFFICE_EMAIL = "galsofer6@gmail.com"
    OFFICE_ADDRESS = "בעלי המלאכה 205, נתיבות"
    OFFICE_WEBSITE = "broadcust.co.il/business/IgalSoferADV"

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


