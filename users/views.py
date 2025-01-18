from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
import json

def login_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
        
        user = authenticate(request, username=email, password=password)
        
        if user:
            login(request, user)  # Logs in the user using Django sessions
            return JsonResponse({"message": "Login successful", "status": "success"}, status=200)
        else:
            return JsonResponse({"message": "Invalid email or password", "status": "error"}, status=401)
    return JsonResponse({"message": "Invalid request method"}, status=400)

def register_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({"message": "Username already exists", "status": "error"}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({"message": "Email already exists", "status": "error"}, status=400)
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            return JsonResponse({"message": "User registered successfully", "status": "success"}, status=201)
        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}", "status": "error"}, status=500)
    return JsonResponse({"message": "Invalid request method"}, status=400)


from django.shortcuts import render

def register_view(request):
    if request.method == "GET":
        return render(request, "register.html")  # Correct template name
    elif request.method == "POST":
        # Handle form submission logic here
        pass
