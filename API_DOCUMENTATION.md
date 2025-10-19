# API Documentation - משרד עו"ד ונוטריון יגאל סופר

## 🔐 **התחברות מאובטחת**

### **שיטות אימות:**
1. **API Key** - לשימוש בסיסי
2. **JWT Token** - לשימוש מתקדם עם הרשאות

---

## 📋 **נקודות קצה (Endpoints)**

### **1. התחברות**
```http
POST /api/login
Content-Type: application/json

{
    "username": "yigal",
    "password": "yigal2025"
}
```

**תגובה:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": "yigal"
}
```

### **2. בדיקת בריאות API**
```http
GET /api/health
```

**תגובה:**
```json
{
    "status": "healthy",
    "timestamp": "2025-01-15T14:30:00",
    "version": "1.0.0"
}
```

---

## 📰 **ניהול בלוג**

### **קבלת כל הפרסומים**
```http
GET /api/blog/posts
X-API-Key: yigal-law-api-2025
```

### **יצירת פרסום חדש**
```http
POST /api/blog/posts
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
    "title": "כותרת הפרסום",
    "content": "תוכן הפרסום...",
    "image": "https://example.com/image.jpg"
}
```

### **עדכון פרסום קיים**
```http
PUT /api/blog/posts/1
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
    "title": "כותרת מעודכנת",
    "content": "תוכן מעודכן..."
}
```

### **מחיקת פרסום**
```http
DELETE /api/blog/posts/1
Authorization: Bearer <JWT_TOKEN>
```

---

## 📞 **ניהול פניות**

### **קבלת כל הפניות**
```http
GET /api/contacts
X-API-Key: yigal-law-api-2025
```

---

## 📊 **סטטיסטיקות**

### **קבלת סטטיסטיקות האתר**
```http
GET /api/stats
X-API-Key: yigal-law-api-2025
```

**תגובה:**
```json
{
    "stats": {
        "years_experience": 30,
        "total_visits": 1250,
        "contact_submissions": 45,
        "blog_posts": 3
    }
}
```

---

## 🔑 **מפתחות API**

### **משתמשים מוגדרים:**
- **admin** / admin123
- **yigal** / yigal2025  
- **manager** / manager123

### **API Key:**
```
yigal-law-api-2025
```

---

## 🚀 **איך להתחיל**

### **1. התקנת התלויות:**
```bash
pip install -r requirements.txt
```

### **2. הפעלת השרת:**
```bash
python api.py
```

### **3. בדיקת החיבור:**
```bash
curl http://localhost:5000/api/health
```

### **4. התחברות:**
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "yigal", "password": "yigal2025"}'
```

---

## 📝 **דוגמאות שימוש**

### **JavaScript/Fetch:**
```javascript
// התחברות
const loginResponse = await fetch('/api/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        username: 'yigal',
        password: 'yigal2025'
    })
});

const { access_token } = await loginResponse.json();

// קבלת פרסומים
const postsResponse = await fetch('/api/blog/posts', {
    headers: {
        'X-API-Key': 'yigal-law-api-2025'
    }
});

const posts = await postsResponse.json();
```

### **Python/Requests:**
```python
import requests

# התחברות
login_data = {
    "username": "yigal",
    "password": "yigal2025"
}
response = requests.post('http://localhost:5000/api/login', json=login_data)
token = response.json()['access_token']

# קבלת פרסומים
headers = {'Authorization': f'Bearer {token}'}
posts = requests.get('http://localhost:5000/api/blog/posts', headers=headers)
```

---

## ⚠️ **אבטחה**

- **שנה את הסיסמאות** בסביבת ייצור
- **השתמש ב-HTTPS** בסביבת ייצור
- **שמור על מפתחות API** בסוד
- **הגבל גישה** לשרתים מורשים בלבד

---

## 🔧 **הגדרות סביבה**

צור קובץ `.env` עם:
```
JWT_SECRET_KEY=your-super-secret-jwt-key
API_KEY=your-custom-api-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```
