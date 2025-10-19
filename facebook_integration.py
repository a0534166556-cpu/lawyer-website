import feedparser
import requests
from datetime import datetime
import os

def get_facebook_posts():
    """
    מקבל פוסטים מ-Facebook RSS feed
    """
    try:
        # Facebook RSS feed URL (צריך להחליף עם ה-URL האמיתי)
        facebook_rss_url = "https://www.facebook.com/feeds/page.php?id=YOUR_PAGE_ID&format=rss20"
        
        # קריאת ה-RSS feed
        feed = feedparser.parse(facebook_rss_url)
        
        posts = []
        for entry in feed.entries[:5]:  # 5 פוסטים אחרונים
            post = {
                'title': entry.get('title', ''),
                'description': entry.get('description', ''),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'image_url': extract_image_from_description(entry.get('description', ''))
            }
            posts.append(post)
        
        return posts
        
    except Exception as e:
        print(f"שגיאה בקבלת פוסטים מ-Facebook: {e}")
        return []

def extract_image_from_description(description):
    """
    מחלץ URL של תמונה מתיאור הפוסט
    """
    try:
        # חיפוש תמונות בתיאור
        import re
        img_pattern = r'<img[^>]+src="([^"]+)"'
        matches = re.findall(img_pattern, description)
        
        if matches:
            return matches[0]  # תמונה ראשונה
        return None
        
    except Exception as e:
        print(f"שגיאה בחילוץ תמונה: {e}")
        return None

def save_facebook_images():
    """
    שומר תמונות מ-Facebook לתיקיית הגלריה
    """
    try:
        posts = get_facebook_posts()
        saved_images = []
        
        for i, post in enumerate(posts):
            if post['image_url']:
                # הורדת התמונה
                response = requests.get(post['image_url'])
                if response.status_code == 200:
                    # שמירת התמונה
                    filename = f"facebook_post_{i+1}.jpg"
                    filepath = os.path.join('static', 'img', 'gallery', filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    saved_images.append({
                        'filename': filename,
                        'title': post['title'],
                        'description': post['description'][:100] + '...' if len(post['description']) > 100 else post['description']
                    })
        
        return saved_images
        
    except Exception as e:
        print(f"שגיאה בשמירת תמונות: {e}")
        return []
