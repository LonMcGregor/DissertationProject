import re

from django.core.files.base import ContentFile
from django.db import transaction

import student.models as m

"""File containing the various pipelines for uploading files"""


def python_solution():
    """When a solution file is uploaded, save it
    then process it accordingly"""
    pass


def python_test_case():
    pass


@transaction.atomic()
def python_results(content, tm):
    """Take in the @content from running a
    @tm test match instance, process this, and save it,
    passing back a model reference"""

    content2 = re.sub(r"(File [\"\']).+/(python[0-9\.]+)/(.+[\"\'])", r"\1/\2/\3", content)
    content3 = re.sub(r"(File [\"\']).+\/var\/tmp\/(.+[\"\'])", r"\1/\2", content2)

    result_sub = m.Submission(id=m.new_random_slug(m.Submission),
                              coursework=tm.coursework,
                              creator=tm.initiator,
                              type=m.SubmissionType.TEST_RESULT)
    result_sub.save()
    result_file = m.File(submission=result_sub)
    result_file.file.save('results.txt', ContentFile(content))
    result_file.save()


