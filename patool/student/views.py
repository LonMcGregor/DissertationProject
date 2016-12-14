from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from student.models import StoredSolution


@login_required(login_url='login')
def index(request):
    return render(request, 'student/index.html')


@login_required(login_url='login')
def upload_solution(request):
    if request.method == 'POST':
        newsol = StoredSolution(file=request.FILES['chosenfile'])
        newsol.save()
        return render(request, 'student/upload_solution.html')
    else:
        return render(request, 'student/upload_solution.html')


def push_test(request):
    return render(request, 'student/pushtest.html')
