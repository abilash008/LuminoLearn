# # chatbot/views.py

# import requests
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
# from django.conf import settings
# from django.views.decorators.http import require_POST


# HF_API_TOKEN = getattr(settings, 'HF_API_TOKEN', None)


# @login_required
# def chatbot_ui(request):
#     return render(request, 'chatbot/chatbot.html')

# @csrf_exempt
# @require_POST
# @login_required
# def chatbot_respond(request):
#     try:
#         # Get message from POST data
#         user_message = request.POST.get('message', '').strip()
#         if not user_message:
#             return JsonResponse({'error': 'No message provided'}, status=400)

#         # Prepare Hugging Face API request
#         headers = {
#             "Authorization": f"Bearer {settings.HF_API_TOKEN}",
#             "Content-Type": "application/json"
#         }

#         payload = {
#             "inputs": user_message,
#             "parameters": {
#                 "max_new_tokens": 200,
#                 "temperature": 0.7,
#                 "return_full_text": False
#             }
#         }

#         # Make API call
#         response = requests.post(
#             "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta",
#             headers=headers,
#             json=payload,
#             timeout=30  # Add timeout
#         )

#         # Handle response
#         if response.status_code == 200:
#             result = response.json()
#             if isinstance(result, list) and len(result) > 0:
#                 return JsonResponse({
#                     'reply': result[0]['generated_text']
#                 })
#             return JsonResponse({
#                 'error': 'Unexpected response format'
#             }, status=500)

#         return JsonResponse({
#             'error': f'API Error: {response.text}',
#             'status': response.status_code
#         }, status=response.status_code)

#     except requests.Timeout:
#         return JsonResponse({
#             'error': 'Request timeout - please try again'
#         }, status=504)
#     except Exception as e:
#         return JsonResponse({
#             'error': str(e)
#         }, status=500)







# chatbot/views.py
import cohere
import markdown
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.http import require_POST
from .models import ChatSession, ChatMessage

def format_response(text):
    """Convert markdown to HTML and add DeepSeek-style formatting"""
    html = markdown.markdown(text)
    # Add additional formatting classes
    html = html.replace('<ul>', '<ul class="dsk-list">') \
            .replace('<ol>', '<ol class="dsk-list">') \
            .replace('<code>', '<pre class="dsk-code"><code>') \
            .replace('</code>', '</code></pre>')
    return html
@login_required
def chatbot_ui(request):
    # Get or create chat session
    session, _ = ChatSession.objects.get_or_create(user=request.user)
    messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
    return render(request, 'chatbot/chatbot.html', {'messages': messages})

@csrf_exempt
@require_POST
@login_required
def chatbot_respond(request):
    try:
        user = request.user
        user_message = request.POST.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)

        # Get or create chat session
        session, _ = ChatSession.objects.get_or_create(user=user)
        
        # Save user message
        ChatMessage.objects.create(session=session, author='user', content=user_message)

        # Get conversation history (last 6 messages)
        history_messages = ChatMessage.objects.filter(session=session).order_by('-timestamp')[:6]
        
        # Format history for Cohere
        history = [
            {"role": "USER" if msg.author == "user" else "CHATBOT", "message": msg.content}
            for msg in reversed(history_messages)
        ]

        # Generate response with Cohere
        co = cohere.Client(settings.COHERE_API_KEY)
        response = co.chat(
            message=user_message,
            model="command",
            chat_history=history,
            preamble="""You are LuminoLearn Tutor. Format responses using Markdown:
            
            **Key Points**:
            - Use bullet points for lists
            - Put code in ``` blocks
            - Use headings for sections
            - Be concise but thorough
            
            Example format:
            **Variable Scoping**
            
            - Global scope: Accessible everywhere
            - Local scope: Only within function
            
            ```python
            def example():
                x = 10  # Local variable
            ```""",
            temperature=0.3,
            citation_quality="accurate"
        )

        formatted_reply = format_response(response.text)
        ChatMessage.objects.create(session=session, author='bot', content=formatted_reply)

        return JsonResponse({'reply': formatted_reply})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)