import requests
import json
import feedparser
from datetime import datetime
import os

class FacebookRSSReader:
    def __init__(self):
        # קורא הגדרות מקובץ ההגדרות
        try:
            from facebook_config import FACEBOOK_PAGE_ID, FACEBOOK_ACCESS_TOKEN, FACEBOOK_PAGE_URL
            self.page_id = FACEBOOK_PAGE_ID if FACEBOOK_PAGE_ID != "YOUR_PAGE_ID_HERE" else None
            self.access_token = FACEBOOK_ACCESS_TOKEN if FACEBOOK_ACCESS_TOKEN != "YOUR_ACCESS_TOKEN_HERE" else None
            self.page_url = FACEBOOK_PAGE_URL if FACEBOOK_PAGE_URL != "https://www.facebook.com/YourPageName" else None
        except ImportError:
            self.page_id = None
            self.access_token = None
            self.page_url = None
        
    def get_facebook_posts_via_rss(self, page_url):
        """
        קורא פוסטים מ-RSS Feed של עמוד פייסבוק
        """
        try:
            # פייסבוק מספק RSS Feed לכל עמוד
            rss_url = f"{page_url}/feed"
            feed = feedparser.parse(rss_url)
            
            posts = []
            for entry in feed.entries[:10]:  # 10 פוסטים אחרונים
                post = {
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.summary,
                    'published': entry.published,
                    'image': self.extract_image_from_entry(entry)
                }
                posts.append(post)
            
            return posts
            
        except Exception as e:
            print(f"שגיאה בקריאת RSS: {e}")
            return []
    
    def extract_image_from_entry(self, entry):
        """
        מחלץ תמונה מהפוסט
        """
        try:
            # מחפש תמונות בתוכן הפוסט
            if hasattr(entry, 'content'):
                content = entry.content[0].value if entry.content else ""
                # חיפוש תמונות ב-HTML
                import re
                img_pattern = r'<img[^>]+src="([^"]+)"'
                matches = re.findall(img_pattern, content)
                if matches:
                    return matches[0]
            
            # אם אין תמונה, מחזיר תמונה ברירת מחדל
            return "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?w=400&h=250&fit=crop"
            
        except:
            return "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?w=400&h=250&fit=crop"
    
    def get_facebook_posts_via_api(self):
        """
        שיטה מתקדמת יותר עם Facebook Graph API
        """
        if not self.page_id or not self.access_token:
            print("צריך להגדיר Page ID ו-Access Token")
            return []
        
        try:
            # Facebook Graph API endpoint
            url = f"https://graph.facebook.com/v18.0/{self.page_id}/posts"
            params = {
                'access_token': self.access_token,
                'fields': 'message,created_time,permalink_url,attachments{media,subattachments}',
                'limit': 10
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                posts = []
                
                for post in data.get('data', []):
                    post_data = {
                        'title': post.get('message', '')[:100] + '...' if len(post.get('message', '')) > 100 else post.get('message', ''),
                        'link': post.get('permalink_url', ''),
                        'description': post.get('message', ''),
                        'published': post.get('created_time', ''),
                        'image': self.extract_image_from_api_post(post)
                    }
                    posts.append(post_data)
                
                return posts
            else:
                print(f"שגיאה ב-API: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"שגיאה בקריאת API: {e}")
            return []
    
    def extract_image_from_api_post(self, post):
        """
        מחלץ תמונה מפוסט API
        """
        try:
            attachments = post.get('attachments', {})
            if attachments:
                data = attachments.get('data', [])
                if data:
                    media = data[0].get('media', {})
                    if media:
                        return media.get('image', {}).get('src', '')
            
            return "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?w=400&h=250&fit=crop"
            
        except:
            return "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?w=400&h=250&fit=crop"

def get_facebook_posts():
    """
    פונקציה ראשית שמחזירה פוסטים מהפייסבוק
    """
    reader = FacebookRSSReader()
    
    # אם יש הגדרות, ננסה לקרוא מהפייסבוק
    if reader.page_url:
        posts = reader.get_facebook_posts_via_rss(reader.page_url)
        
        if not posts and reader.page_id and reader.access_token:
            # שיטה 2: API (מתקדם יותר)
            posts = reader.get_facebook_posts_via_api()
        
        return posts
    
    # אם אין הגדרות, מחזיר רשימה ריקה
    return []

def get_page_id_from_url(page_url):
    """
    מנסה למצוא Page ID מה-URL של העמוד
    """
    try:
        import re
        
        # מנסה לחלץ מספרים מה-URL
        numbers = re.findall(r'\d+', page_url)
        if numbers:
            return numbers[0]
        
        # אם לא מצא מספרים, מנסה דרך אחרת
        return None
        
    except:
        return None

if __name__ == "__main__":
    # דוגמה לשימוש
    print("בודק פייסבוק...")
    
    # ננסה למצוא Page ID
    page_url = "https://www.facebook.com/IgalSoferADV/"
    page_id = get_page_id_from_url(page_url)
    print(f"Page URL: {page_url}")
    print(f"Page ID שנמצא: {page_id}")
    
    posts = get_facebook_posts()
    if posts:
        print(f"נמצאו {len(posts)} פוסטים:")
        for post in posts:
            print(f"כותרת: {post['title']}")
            print(f"קישור: {post['link']}")
            print(f"תמונה: {post['image']}")
            print("---")
    else:
        print("לא נמצאו פוסטים. ייתכן שצריך להגדיר Page ID ב-facebook_config.py")
