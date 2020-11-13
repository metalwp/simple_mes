from django.shortcuts import render, redirect, reverse

# Create your views here.


def index(request):
    user = request.user
    if user.is_authenticated:
        return render(request, 'dashboard/index.html')
    else:
        request.session['errMsg'] = '请先登陆！'
        return redirect(reverse('account:login'))

