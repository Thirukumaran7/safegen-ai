import os
from google import genai

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    api_key = 'AIzaSyCC6Kun0OT_7l9MnnSuQSSnY-mT4xMexFQ'

try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='say hello in one word'
    )
    print('API KEY WORKING')
    print('Response:', response.text)
except Exception as e:
    print('API KEY FAILED')
    print('Error:', str(e))
