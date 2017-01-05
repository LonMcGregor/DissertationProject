from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
import teacher.permission as p

@login_required()
@p.is_teacher
def index(request):
    return render(request, 'teacher/index.html')
