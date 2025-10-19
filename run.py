#!/usr/bin/env python3
"""
הפעלת האתר של משרד עו"ד ונוטריון יגאל סופר
"""

import os
from app import app

if __name__ == '__main__':
    # הגדרות לפיתוח
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("🚀 מפעיל את האתר של משרד עו\"ד ונוטריון יגאל סופר...")
    print(f"📍 האתר זמין בכתובת: http://localhost:{port}")
    print("⚖️ משרד עו\"ד ונוטריון יגאל סופר - נתיבות")
    print("📞 08-993-1666 | ✉️ galsofer6@gmail.com")
    print("-" * 50)
    
    # הפעלה ללא dotenv
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        load_dotenv=False
    )
