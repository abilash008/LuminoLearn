import json
import requests
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required
def code_editor(request):
    """
    Renders the code editor page with a list of supported languages.
    """
    supported_languages = [
        {'name': 'Python', 'value': 'python3'},
        {'name': 'JavaScript', 'value': 'javascript'},
        {'name': 'Java', 'value': 'java'},
        {'name': 'C++', 'value': 'cpp'},
    ]
    return render(request, 'student/editor.html', {'languages': supported_languages})

@csrf_exempt  # Optionally remove this if you'd rather handle CSRF differently.
@login_required
def execute_code(request):
    """
    Receives code & language via JSON, sends it to JDoodle, and returns the result.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')
            language = data.get('language', 'python')
            
            
            # JDoodle credentials from settings
            client_id = getattr(settings, 'JDOODLE_CLIENT_ID', None)
            client_secret = getattr(settings, 'JDOODLE_CLIENT_SECRET', None)
            
            if not client_id or not client_secret:
                return JsonResponse({"error": "JDoodle credentials not set in settings."}, status=500)
            
            payload = {
                'clientId': client_id,
                'clientSecret': client_secret,
                'script': code,
                'language': language,
                'versionIndex': '0',
                
            }
            
            response = requests.post('https://api.jdoodle.com/v1/execute', json=payload)
            result = response.json()
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)
