#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# הוסף את התיקייה הנוכחית ל-PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    
    print("🚀 מפעיל את האתר של משרד עו\"ד ונוטריון יגאל סופר...")
    print("📍 האתר זמין בכתובת: http://localhost:5000")
    print("⚖️ משרד עו\"ד ונוטריון יגאל סופר - נתיבות")
    print("📞 08-993-1666 | ✉️ galsofer6@gmail.com")
    print("-" * 50)
    print("לעצור את השרת: Ctrl+C")
    print("-" * 50)
    
    # הפעל את השרת
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000,
        load_dotenv=False,
        use_reloader=False
    )
    
except ImportError as e:
    print(f"❌ שגיאה בייבוא: {e}")
    print("אנא וודא שכל הקבצים נמצאים בתיקייה הנכונה")
except Exception as e:
    print(f"❌ שגיאה: {e}")
    print("אנא בדוק את הקוד ונסה שוב")


