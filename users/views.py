from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .models import CustomUser
from django.contrib.auth.decorators import login_required

@csrf_exempt
def login_view(request):
    """
    Handles user login requests.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Please enter both email and password.")
            return redirect("login")  # Redirect back to the login page

        # Authenticate user
        user = authenticate(request, username=username, password=password)  # Using `username` as email by default
        if user:
            login(request, user)  # Log the user in using Django sessions

            # Redirect based on role
            if user.role == "student":
                return redirect("student_dashboard")
            elif user.role == "educator":
                return redirect("educator_dashboard")
            elif user.role == "admin":
                return redirect("admin_dashboard")
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("login")  # Redirect back to the login page

    # Handle GET requests to render the login page
    return render(request, "login.html")  # Render the login template


@csrf_exempt
def register_view(request):
    User = get_user_model()
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        role = request.POST["role"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        # Validation
        if not username or not email or not password or not confirm_password:
            messages.info(request, "Please fill in all fields.")
            return redirect("register")
        if password != confirm_password:
            messages.info(request, "Passwords do not match.")
            return redirect("register")
        if User.objects.filter(username=username).exists():
            messages.info(request, "Username already exists.")
            return redirect("register")
        if User.objects.filter(email=email).exists():
            messages.info(request, "Email already exists.")
            return redirect("register")
        if not role:
            messages.info(request, "Please select a role.")
            return redirect("register")
        if role not in ["student", "educator", "admin"]:
            messages.info(request, "Invalid role")
            return redirect("register")


        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password, role=role)
        user.save()
        
        user.role = role  # Assuming a related Profile model
        user.save()
        
        messages.info(request, "User created successfully")
        return redirect("login")
    
    # Render the registration page for GET requests
    return render(request, "register.html")



@login_required
def dashboard_view(request):
    user = request.user  # Get the logged-in user
    role = user.role  # Get the role of the user from CustomUser

    context = {"user": user, "role": role}

    if role == "student":
        return render(request,"student_dashboard.html")
    elif role == "educator":
        return render(request,"educator_dashboard.html")
    elif role == "admin":
        return render(request,"admin_dashboard.html")

    #return render(request, "dashboard.html", context)



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



from django.contrib.auth import logout
from django.shortcuts import redirect

@csrf_exempt
def logout_view(request):
    if request.method == "POST":
        logout(request)  # Log the user out
        return redirect(request,"login.html")
