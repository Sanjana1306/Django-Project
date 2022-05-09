from base64 import urlsafe_b64decode, urlsafe_b64encode
from email.message import EmailMessage
from os import link
from telnetlib import LOGOUT
from django.shortcuts import redirect,render
from django.shortcuts import render
from django import http
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate , login,logout
from django.shortcuts import render
from SD import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_str
from SD.info import EMAIL_HOST_USER
from . tokens import generate_token
from django.urls import reverse



def base(request):
    if request.method == "POST":
        username=request.POST['username']
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']

        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name= fname
        myuser.last_name=lname
        myuser.save()

        messages.success(request,"Your Account has been successfully created.")

        return redirect('signin')

    else:
         return render(request,"authentication/base.html")

def home(request):
    return render(request,"authentication/index.html") 

def signup(request):
    if request.method == "POST":                
        username=request.POST['username']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']  
        fname=request.POST['fname']          

    
        if User.objects.filter(username = username).first():
            messages.error(request, "This username is already taken, Please try something else")
            return redirect('signup')

        if User.objects.filter(email= email):
            messages.error(request, "Email already registered!")
            return redirect('signup')

        if len(username)>10:
            messages.error(request,"Username must under 10 characters. ")
            return redirect('signup')
        
        if pass1 != pass2:
            messages.error(request,"Password doesn't match, Check Again")
            return redirect('signup')
        
        if not username.isalnum():
            messages.error(request,"Username must be Alpha-numeric!!")
            return redirect('signup')

       
        myuser = User.objects.create_user(username,email,pass1)
        myuser.set_password(pass1)
        myuser.first_name=fname
        #myuser.is_active=False
        myuser.save()

        messages.success(request, 'Your account successfully created ! We have sent you a confirmation mail for sign in!!') 
        messages.success(request,'Please confirm your email in order to activate your account.')

        #Welcome Email

        current_site=get_current_site(request)
        domain =current_site.domain
        uid = urlsafe_b64encode(force_bytes(myuser.pk))
        token =generate_token.make_token(myuser)
        from_email=settings.EMAIL_HOST_USER
        to_list= [myuser.email]

        link = reverse('activate',kwargs={'uidb64':uid , 'token':token})
        url_= 'http://'+ domain + link
        
        subject="Account Verification for MusicPlayer!!"
        message = "Hello " + myuser.first_name+ " !! \n" + "Welcome to Portal.Thank You for visiting our website.\n Click on the below link to activate your account\n" + url_ +   "\n\n Regards,\n Team P-13"
        send_mail(subject , message, from_email , to_list , fail_silently=True)

        #Email Address Confirmation Email        
        
        
        '''current_site=get_current_site(request)
        email_subject="Confirm your Email Address"
        message2=render_to_string('email_confirm.html',{
            'name': myuser.first_name,
            'domain':current_site.domain,
            'uid': urlsafe_b64encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser)
        })
        email=EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )

        email.send(fail_silently=False)
        #email.fail_silently=True
        #email.send()'''
        return redirect('signin')   

    else:
        return render(request, "authentication/signup.html")

     
def signin(request):
    if request.method=="POST":
        username = request.POST['username']
        password1 = request.POST['pass1']

        user = authenticate(username = username , password = password1 )

        if user is not None:
            login(request,user)
            fname = user.get_username
            return render(request,"authentication/Page.html", {'fname':fname})
   
        else:
            messages.info(request,'Bad Credentials,Account doesn\'t  exist please sign up!!!')
            return redirect('home')
        
    return render(request ,'authentication/signin.html')


def signout(request):  
    logout(request)
    return redirect('home')

def Page(request):
    return render(request,"authentication/Page.html")
 

def activate(request,uidb64 ,token):
    try:
         uid=force_str(urlsafe_b64decode(uidb64))
         myuser = User.objects.get(pk=uid)
    except(TypeError, ValueError , OverflowError,User.DoesNotExist):
        myuser=None
    
    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active=True
        myuser.save()
        login(request,myuser)
        return redirect('home')
    else:
        return render(request,'activation_failed.html')

