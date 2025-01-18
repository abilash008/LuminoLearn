from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate
from django.http import JsonResponse

def login_view(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
        
        user = authenticate(request, username=email, password=password)
        
        if user:
            # Assuming you're using Django sessions for authentication
            from django.contrib.auth import login
            login(request, user)
            return JsonResponse({"message": "Login successful", "status": "success"}, status=200)
        else:
            return JsonResponse({"message": "Invalid email or password", "status": "error"}, status=401)
    return JsonResponse({"message": "Invalid request method"}, status=400)

