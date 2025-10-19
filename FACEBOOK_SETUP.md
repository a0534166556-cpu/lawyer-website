# הגדרת חיבור לפייסבוק

## איך להגדיר את החיבור לפייסבוק:

### שלב 1: מצא את Page ID של העמוד בפייסבוק
1. לך לעמוד הפייסבוק שלך
2. לחץ על "About" (אודות)
3. גלול למטה עד "Page Info" (מידע על העמוד)
4. העתק את ה-Page ID (מספר ארוך)

### שלב 2: עדכן את הקובץ facebook_config.py
פתח את הקובץ `facebook_config.py` ועדכן:

```python
# החלף את הערכים הבאים:
FACEBOOK_PAGE_ID = "123456789012345"  # Page ID שמצאת
FACEBOOK_PAGE_URL = "https://www.facebook.com/YourPageName"  # URL של העמוד
```

### שלב 3: (אופציונלי) קבל Access Token
אם אתה רוצה שימוש מתקדם יותר:

1. לך ל: https://developers.facebook.com/tools/explorer/
2. בחר את האפליקציה שלך (או צור חדשה)
3. בחר "Get Page Access Token"
4. העתק את ה-Token
5. עדכן ב-`facebook_config.py`:
```python
FACEBOOK_ACCESS_TOKEN = "your_access_token_here"
```

### שלב 4: התקן חבילות נוספות
הפעל:
```bash
pip install feedparser requests
```

### איך זה עובד:
- **RSS Feed**: פייסבוק מספק RSS Feed לכל עמוד - זה הכי פשוט
- **API**: שיטה מתקדמת יותר שמאפשרת יותר שליטה
- **Fallback**: אם הפייסבוק לא עובד, האתר יציג את המאמרים הסטטיים

### בדיקה:
לאחר ההגדרה, רענן את דף "כל הפרסומים" - אמור לראות את הפוסטים מהפייסבוק!

## בעיות נפוצות:
1. **אין פוסטים**: וודא שה-Page ID נכון
2. **שגיאות**: בדוק שה-URL של העמוד נכון
3. **תמונות לא מוצגות**: זה נורמלי - האתר ישתמש בתמונות ברירת מחדל
