from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
from .models import CustomUser

@csrf_exempt
def login_view(request):
    """
    Handles user login requests.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")
            
            # Authenticate user
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)  # Log the user in using Django sessions
                return JsonResponse({"message": "Login successful", "status": "success"}, status=200)
            else:
                return JsonResponse({"message": "Invalid email or password", "status": "error"}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data", "status": "error"}, status=400)
    return JsonResponse({"message": "Invalid request method", "status": "error"}, status=405)

@csrf_exempt
def register_view(request):
    """
    Handles user registration requests (API-based).
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            email = data.get("email")
            role = data.get("role")
            password = data.get("password")
            confirm_password = data.get("confirm_password")

            # Validation
            if not username or not email or not password or not confirm_password:
                return JsonResponse({"message": "All fields are required", "status": "error"}, status=400)
            if password != confirm_password:
                return JsonResponse({"message": "Passwords do not match", "status": "error"}, status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({"message": "Username already exists", "status": "error"}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({"message": "Email already exists", "status": "error"}, status=400)
            if not role:
                return JsonResponse({"message": "Role is required", "status": "error"}, status=400)
            if role not in ["student", "educator", "admin"]:
                return JsonResponse({"message": "Invalid role", "status": "error"}, status=400)
            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({"message": "Username already exists", "status": "error"}, status=400)
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({"message": "Email already exists", "status": "error"}, status=400)


            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password, role=role)
            user.save()
            
            user.profile.role = role  # Assuming a related Profile model
            user.profile.save()
            
            return JsonResponse({"message": "User registered successfully", "status": "success"}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data", "status": "error"}, status=400)
        except Exception as e:
            return JsonResponse({"message": f"An error occurred: {str(e)}", "status": "error"}, status=500)
    return JsonResponse({"message": "Invalid request method", "status": "error"}, status=405)

def register_form_view(request):
    """
    Handles rendering of the registration form (for web-based frontend).
    """
    if request.method == "GET":
        return render(request, "register.html")  # Ensure "register.html" exists in your templates folder
    elif request.method == "POST":
        # If handling form submission (non-API), logic can be added here
        return JsonResponse({"message": "Form submission not yet implemented"}, status=501)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard_view(request):
    user = request.user  # Get the logged-in user
    role = user.role  # Get the role of the user from CustomUser

    context = {"user": user, "role": role}

    if role == "student":
        context["message"] = "Welcome to the Student Dashboard!"
    elif role == "educator":
        context["message"] = "Welcome to the Educator Dashboard!"
    elif role == "admin":
        context["message"] = "Welcome to the Admin Dashboard!"

    return render(request, "dashboard.html", context)



from .decorators import role_required

@login_required
@role_required(["student"])
def student_dashboard_view(request):
    return render(request, "student_dashboard.html")

@login_required
@role_required(["educator"])
def educator_dashboard_view(request):
    return render(request, "educator_dashboard.html")

@login_required
@role_required(["admin"])
def admin_dashboard_view(request):
    return render(request, "admin_dashboard.html")
