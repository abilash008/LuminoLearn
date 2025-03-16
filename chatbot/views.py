# chatbot/views.py

import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.http import require_POST


HF_API_TOKEN = getattr(settings, 'HF_API_TOKEN', None)


@login_required
def chatbot_ui(request):
    return render(request, 'chatbot/chatbot.html')

@csrf_exempt
@require_POST
@login_required
def chatbot_respond(request):
    try:
        # Get message from POST data
        user_message = request.POST.get('message', '').strip()
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)

        # Prepare Hugging Face API request
        headers = {
            "Authorization": f"Bearer {settings.HF_API_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": user_message,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "return_full_text": False
            }
        }

        # Make API call
        response = requests.post(
            "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta",
            headers=headers,
            json=payload,
            timeout=30  # Add timeout
        )

        # Handle response
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return JsonResponse({
                    'reply': result[0]['generated_text']
                })
            return JsonResponse({
                'error': 'Unexpected response format'
            }, status=500)

        return JsonResponse({
            'error': f'API Error: {response.text}',
            'status': response.status_code
        }, status=response.status_code)

    except requests.Timeout:
        return JsonResponse({
            'error': 'Request timeout - please try again'
        }, status=504)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)