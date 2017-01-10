from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import student.models as m
import student.permission as p
import student.forms as f


@login_required()
def index(request):
    return render(request, 'student/index.html')


@login_required()
@p.cw_exists_for_upload
def upload_solution(request, singlecw=None):
    # todo verify the upload should occur
    if singlecw is None or singlecw == "":
        return Http404()
    if request.method == 'POST':
        cw = m.Coursework.objects.get(id=singlecw)
        s = m.File(coursework=cw, creator=request.user, filepath=request.FILES['chosen_file'],
                   type=request.POST['file_type'])
        s.save()
        detail = {
            "is_upload": True,
            "filename": request.FILES['chosen_file'],
            "cw": singlecw,
            "ff": f.FileUploadForm
        }
    else:
        detail = {
            "is_upload": False,
            "cw": singlecw,
            "ff": f.FileUploadForm
        }
    return render(request, 'student/upload_solution.html', detail)


@login_required()
def upload_test(request, singlecw):
    if singlecw is None or singlecw == "":
        return Http404()
    if not p.can_view_coursework(request.user, singlecw):
        return HttpResponseForbidden()


def retrieve_coursework(request):
    """For a given @request, return a list of courseworks available to the user"""
    logged_in_user = request.user
    enrolled_courses = m.EnrolledUser.objects.filter(login=logged_in_user).values('course')
    courses_for_user = m.Course.objects.filter(id__in=enrolled_courses)
    all_courseworks_for_user = m.Coursework.objects.filter(course__in=courses_for_user)
    visible_courseworks = []
    for item in all_courseworks_for_user:
        if p.can_view_coursework(logged_in_user, item):
            visible_courseworks.append(item)
    return all_courseworks_for_user.values_list('id', 'state', 'course', 'name').order_by(
        'state') # todo this thing


@login_required()
def detail_coursework(request, singlecw=None):
    if singlecw is None or singlecw == "":
        available = retrieve_coursework(request)
        return render(request, 'student/choose_coursework.html', {'courseworks': available})
    cw = m.Coursework.objects.get(id=singlecw)
    #if not p.can_view_coursework(request.user, cw):
    #    return HttpResponseForbidden
    #check submission status
    me = request.user
    #sol = m.FILE.objects.filter(developer=me).count() != 0
    sol = False
    test = False
    test_run = False
    ass = False
    details = {
        "cw": cw,
        "solution": sol,
        "test": test,
        "testrun": test_run,
        "assess": ass
    }
    return render(request, 'student/detail_coursework.html', details)
