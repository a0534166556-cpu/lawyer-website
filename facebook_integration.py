import requests
import json
from datetime import datetime
import os

def get_facebook_posts():
    """
    מקבל פוסטים מ-Facebook באמצעות Graph API
    """
    try:
        # Facebook Page ID (צריך להחליף עם ה-ID האמיתי)
        page_id = "IgalSoferADV"
        
        # Access Token (צריך להגדיר)
        access_token = "YOUR_ACCESS_TOKEN"
        
        # Facebook Graph API URL
        url = f"https://graph.facebook.com/v18.0/{page_id}/posts"
        params = {
            'access_token': access_token,
            'fields': 'message,created_time,full_picture,link',
            'limit': 10
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            posts = []
            
            for post in data.get('data', []):
                post_data = {
                    'title': post.get('message', '')[:100] + '...' if len(post.get('message', '')) > 100 else post.get('message', ''),
                    'description': post.get('message', ''),
                    'link': post.get('link', ''),
                    'published': post.get('created_time', ''),
                    'image_url': post.get('full_picture', '')
                }
                posts.append(post_data)
            
            return posts
        else:
            print(f"Facebook API error: {response.status_code}")
            return []
        
    except Exception as e:
        print(f"שגיאה בקבלת פוסטים מ-Facebook: {e}")
        return []

def save_facebook_images():
    """
    שומר תמונות מ-Facebook לתיקיית הגלריה
    """
    try:
        posts = get_facebook_posts()
        saved_images = []
        
        for i, post in enumerate(posts):
            if post['image_url']:
                try:
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
                except Exception as e:
                    print(f"שגיאה בשמירת תמונה {i+1}: {e}")
                    continue
        
        return saved_images
        
    except Exception as e:
        print(f"שגיאה בשמירת תמונות: {e}")
        return []
