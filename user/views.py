from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_superuser:
                login(request, user)
                return redirect('admin_transactions')
            else:
                return render(request, 'admin_login.html', {'error': 'Invalid credentials or not a superuser.'})
        else:
            return render(request, 'admin_login.html', {'error': 'Invalid form submission.'})
    return render(request, 'admin_login.html')