from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from orders.models import *
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def register_view(request):

    if request.method == 'POST':
        
        try:
            
            first_name = request.POST.get('fname')
            last_name = request.POST.get('lname')
            username = request.POST.get('username')
            email = request.POST.get('email')
            phone_number = request.POST.get('pnumber')
            password = request.POST.get('password')
            cpassword = request.POST.get('cpassword')

            if len(username) <= 7:
                messages.error(request, 'username lenght must be Greater than 8')
                return redirect('register_page')

            if password != cpassword:
                messages.error(request, 'Both passwords should be same')
                return redirect('register_page')
        
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, f'The username {username} is already taken')
                return redirect('register_page')
        
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, f'The email address {email} is already taken')
                return redirect('register_page')
        
            user = CustomUser.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, phone_number=phone_number,password=password)
            user.save()
            messages.success(request, 'successfully registered your account')
            return redirect('login_page')
    
        except Exception as e:

            print(e)
            messages.error(request, 'something went wrong, please try again later.')
            return redirect('register_page')
        
    return render(request, 'signup.html')
    

def login_view(request):

    if request.method == 'POST':

        try:
            email = request.POST.get('email')
            password = request.POST.get('password')

            if not email:
                messages.error(request, 'fill email address')
                return redirect('login_page')

            if not password:
                messages.error(request, 'fill password field')
                return redirect('login_page')

            if not email or not password:
                messages.error(request, 'fill both fields')
                return redirect('login_page')
        
            user = authenticate(username=email, password=password)

            if user is not None:
                login(request,user)
                messages.success(request, 'you have successfully login to your account.')
                return redirect('orders_list')
            
            messages.error(request, 'The user does not exists, please register your account first')
            return redirect('login_page')
    
        except Exception as e:
            print(e)
            messages.error(request, 'something went wrong')
            return redirect('login_page')
        
    return render(request, 'login.html')
    

def logout_view(request):

    try:
        logout(request)
        return redirect('login_view')
    
    except Exception as e:
        print(e)
        messages.success('succesfully logged out your account')
        return redirect('orders_list')