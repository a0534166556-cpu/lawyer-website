# -*- coding: utf-8 -*-
"""
הפעלה פשוטה של האתר
"""

from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'simple-secret-key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    print("🚀 מפעיל את האתר של משרד עו\"ד ונוטריון יגאל סופר...")
    print("📍 האתר זמין בכתובת: http://localhost:5000")
    print("⚖️ משרד עו\"ד ונוטריון יגאל סופר - נתיבות")
    print("📞 08-993-1666 | ✉️ galsofer6@gmail.com")
    print("-" * 50)
    print("לעצור את השרת: Ctrl+C")
    print("-" * 50)
    
    app.run(debug=True, host='127.0.0.1', port=5000)


