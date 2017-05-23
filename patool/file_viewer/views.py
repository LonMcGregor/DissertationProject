from mimetypes import guess_type

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.http.response import FileResponse
from django.shortcuts import render
from pygments import highlight as pyghi
from pygments.formatters import html as pygform
from pygments.lexers import python as pyglex

import file_viewer.permissions as p
from common.helpers import get_file


@login_required()
def download_file(request, sub_id, filename):
    """This is the main public entry point for getting and
    reading a file from the web browser. It looks for the given
    @sub_id and @filename"""
    file = get_file(sub_id, filename)
    if not p.can_view_file(request.user, file):
        return HttpResponseForbidden("You are not allowed to see this file")
    if 'pretty' in request.GET:
        return render_file(request, file, filename)
    if 'show' in request.GET:
        return show_file(file, filename)
    return attachment_file(file, filename)


def render_file(request, file, filename):
    """For a given @file and @filename,  pretty print the contents
    of the file as an HTML page using pygments"""
    mime = guess_type(filename, True)
    if mime[0] is None or mime[0].split('/')[0] != 'text':
        return show_file(file, filename)
    content = file.file.read()
    detail = {
        "content": pyghi(content, pyglex.PythonLexer(), pygform.HtmlFormatter(linenos='table'))
    }
    return render(request, 'file_viewer/pretty_file.html', detail)


def show_file(file, filename):
    """For a given @file/@filename, display this in-browser"""
    response = FileResponse(file.file)
    response['Content-Type'] = str(guess_type(filename, False)[0])
    return response


def attachment_file(file, filename):
    """return a @file fieldfile and @filename as an http attachment"""
    response = FileResponse(file.file)
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response
