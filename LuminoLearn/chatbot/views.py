# chatbot/views.py

import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings

# If using OpenAI, ensure you have OPENAI_API_KEY in your settings or .env
OPENAI_API_KEY = getattr(settings, 'OPENAI_API_KEY', None)

@login_required
def chatbot_ui(request):
    """
    Renders the chatbot UI template.
    """
    return render(request, 'chatbot/chatbot.html')

@csrf_exempt
@login_required
def chatbot_respond(request):
    """
    AJAX endpoint: receives user message, calls external GPT-like API, returns JSON reply.
    """
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)

        # For OpenAI's ChatGPT-like endpoint:
        # We'll send a single message, but you can maintain a conversation array if you want context.
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        data = {
            "model": "gpt-3.5-turbo",  # or "gpt-4", "text-davinci-003", etc.
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            response_json = response.json()
            # Extract the assistant's message
            bot_reply = response_json["choices"][0]["message"]["content"]
            return JsonResponse({"reply": bot_reply})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

# Uncomment and modify if you want to integrate a Hugging Face LLaMA model:
"""
def call_llama_api(user_message):
    # For example, if you have a Hugging Face Inference API:
    HF_API_TOKEN = getattr(settings, 'HF_API_TOKEN', None)
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": user_message,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7
        }
    }
    response = requests.post("https://api-inference.huggingface.co/models/YourOrg/YourLLaMAModel", headers=headers, json=payload)
    result = response.json()
    # Parse result based on Hugging Face's response structure
    return result[0]["generated_text"]  # Example
"""
