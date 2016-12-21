from django.http import Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import student.models as m


@login_required(login_url='login')
def index(request):
    return render(request, 'student/index.html')


@login_required(login_url='login')
def upload_solution(request, singlecw=None):
    #todo verify the upload should occur
    if singlecw is None or singlecw == "":
        return Http404()
    if request.method == 'POST':
        newsol = m.Solution(cwid=singlecw, userid=request.user.id, file=request.FILES[
            'chosenfile'])
        newsol.save()
        detail = {
            "is_upload": True,
            "filename": request.FILES['chosenfile'],
            "cw": singlecw
        }
    else:
        detail = {
            "is_upload": False,
            "cw": singlecw
        }
    return render(request, 'student/upload_solution.html', detail)


def push_test(request):
    return render(request, 'student/pushtest.html')


def retrieve_coursework(request):
    """For a given @request, return a list of courseworks available to the user"""
    logged_in_user = request.user
    available = [("task 1", 123),("task 2", 234), ("task 3", 345)]
    return available


@login_required(login_url='login')
def detail_coursework(request, singlecw=None):
    if singlecw is None or singlecw == "":
        available = retrieve_coursework(request)
        return render(request, 'student/choose_coursework.html', {'courseworks': available})
    details = {
        "name": "binary tree",
        "cwid": singlecw,
        "descript": "http://example.com/descriptor.pdf",
        "completed_submit": False,
        "completed_assess": False
    }
    return render(request, 'student/detail_coursework.html', details)