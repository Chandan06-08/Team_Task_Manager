import requests
from bs4 import BeautifulSoup
import uuid

session = requests.Session()

# 1. Get the CSRF token
response = session.get('http://127.0.0.1:8000/signup/')
soup = BeautifulSoup(response.text, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

# 2. POST to signup
username = "test_" + uuid.uuid4().hex[:8]
data = {
    'csrfmiddlewaretoken': csrf_token,
    'name': username,
    'email': f'{username}@example.com',
    'password1': 'TestPassword123!',
    'password2': 'TestPassword123!',
}
response = session.post('http://127.0.0.1:8000/signup/', data=data)

# 3. Check the HTML of the response (which should be the dashboard due to redirect)
if "Welcome! Your account has been created." in response.text:
    print("SUCCESS: The message is in the HTML.")
elif 'class="messages"' in response.text:
    print("WARNING: Messages block is there, but not the specific message.")
else:
    print("ERROR: No messages block or text found in the HTML.")
