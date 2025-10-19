"""
הגדרת Facebook API - מדריך מפורט
"""

# שלב 1: צור אפליקציית פייסבוק
# לך ל: https://developers.facebook.com/apps/
# לחץ על "Create App"
# בחר "Business" 
# מלא את הפרטים:
# - App Name: "Igal Sofer Law Office Website"
# - Contact Email: galsofer6@gmail.com

# שלב 2: קבל App ID ו-App Secret
# באפליקציה שיצרת:
# - לך ל-Dashboard
# - העתק את App ID ו-App Secret

# שלב 3: הוסף את Facebook Login
# - לך ל-Add Product
# - הוסף "Facebook Login"
# - הגדר Valid OAuth Redirect URIs: http://localhost:5000/ (לפיתוח)

# שלב 4: קבל Page Access Token
# לך ל: https://developers.facebook.com/tools/explorer/
# בחר את האפליקציה שלך
# לחץ על "Get Token" → "Get Page Access Token"
# בחר את העמוד "IgalSoferADV"
# העתק את ה-Token

# שלב 5: עדכן את facebook_config.py
FACEBOOK_APP_ID = "YOUR_APP_ID_HERE"
FACEBOOK_APP_SECRET = "YOUR_APP_SECRET_HERE"
FACEBOOK_PAGE_ID = "YOUR_PAGE_ID_HERE"
FACEBOOK_ACCESS_TOKEN = "YOUR_PAGE_ACCESS_TOKEN_HERE"

# דוגמה:
# FACEBOOK_APP_ID = "1234567890123456"
# FACEBOOK_APP_SECRET = "abcdef1234567890abcdef1234567890"
# FACEBOOK_PAGE_ID = "987654321098765"
# FACEBOOK_ACCESS_TOKEN = "EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

print("עקוב אחר ההוראות בקובץ הזה כדי להגדיר את Facebook API")
