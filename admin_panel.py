from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired
import os

# Import the main app
from app import app

# Admin credentials (in production, use environment variables)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'yigal2025'

# Blog posts storage (in production, use database)
blog_posts = {
    1: {
        'id': 1,
        'title': 'נזיקין תביעות',
        'author': 'יגאל סופר עורך דין ונוטריון',
        'date': '15/01/2025 14:30',
        'image': 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=400&h=250&fit=crop',
        'content': 'תוכן המאמר...'
    },
    2: {
        'id': 2,
        'title': 'תאונת עבודה מול הביטוח הלאומי',
        'author': 'יגאל סופר עורך דין ונוטריון',
        'date': '22/01/2025 11:15',
        'image': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=400&h=250&fit=crop',
        'content': 'תוכן המאמר...'
    },
    3: {
        'id': 3,
        'title': 'תאונות עם מעורבות של אופניים חשמליים',
        'author': 'יגאל סופר עורך דין ונוטריון',
        'date': '28/01/2025 16:45',
        'image': 'https://images.unsplash.com/photo-1581578731548-c7e3d1c1c9d9?w=400&h=250&fit=crop',
        'content': 'תוכן המאמר...'
    }
}

class BlogPostForm(FlaskForm):
    title = StringField('כותרת המאמר', validators=[DataRequired()])
    content = TextAreaField('תוכן המאמר', validators=[DataRequired()])
    image = StringField('קישור לתמונה')
    submit = SubmitField('שמור')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('התחברת בהצלחה!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('שם משתמש או סיסמה שגויים', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('התנתקת בהצלחה', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    return render_template('admin/dashboard.html', posts=blog_posts)

@app.route('/admin/posts')
def admin_posts():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    return render_template('admin/posts.html', posts=blog_posts)

@app.route('/admin/posts/new', methods=['GET', 'POST'])
def admin_new_post():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    form = BlogPostForm()
    
    if form.validate_on_submit():
        # Create new post
        new_id = max(blog_posts.keys()) + 1 if blog_posts else 1
        blog_posts[new_id] = {
            'id': new_id,
            'title': form.title.data,
            'author': 'יגאל סופר עורך דין ונוטריון',
            'date': '15/01/2025 14:30',  # In production, use datetime.now()
            'image': form.image.data or 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=400&h=250&fit=crop',
            'content': form.content.data
        }
        
        flash('המאמר נשמר בהצלחה!', 'success')
        return redirect(url_for('admin_posts'))
    
    return render_template('admin/new_post.html', form=form)

@app.route('/admin/posts/<int:post_id>/edit', methods=['GET', 'POST'])
def admin_edit_post(post_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    post = blog_posts.get(post_id)
    if not post:
        flash('מאמר לא נמצא', 'error')
        return redirect(url_for('admin_posts'))
    
    form = BlogPostForm(obj=post)
    
    if form.validate_on_submit():
        blog_posts[post_id].update({
            'title': form.title.data,
            'content': form.content.data,
            'image': form.image.data or post['image']
        })
        
        flash('המאמר עודכן בהצלחה!', 'success')
        return redirect(url_for('admin_posts'))
    
    return render_template('admin/edit_post.html', form=form, post=post)

@app.route('/admin/posts/<int:post_id>/delete', methods=['POST'])
def admin_delete_post(post_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if post_id in blog_posts:
        del blog_posts[post_id]
        flash('המאמר נמחק בהצלחה!', 'success')
    else:
        flash('מאמר לא נמצא', 'error')
    
    return redirect(url_for('admin_posts'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
