import student.models as m


def first_available(coursework, initiator, marker, visible):
    """This method will perform a matching of students.
    this generic method takes solutions and matches them
    to tests on a first-come basis - uses common arguments
    for testmatch objects: @initiator, @marker bool if needed,
    @visible to developer if needed"""
    unassigned_solutions = list(m.Submission.objects.filter(coursework=coursework,
                                                       type=m.SubmissionType.SOLUTION,
                                                       private=False))
    # todo get the submission marked as final
    unassigned_tests = list(m.Submission.objects.filter(coursework=coursework,
                                                   type=m.SubmissionType.TEST_CASE,
                                                   private=False))
    unassigned_users = list(m.EnrolledUser.objects.filter(course=coursework.course))
    for sol in unassigned_solutions:
        chosen_test = None
        chosen_marker = None
        for test in unassigned_tests:
            if sol.creator != test.creator:
                chosen_test = test
                break
        if chosen_test is None:
            raise Exception("Not enough tests available to cover solutions")
        if marker:
            for user in unassigned_users:
                if sol.creator != user:
                    chosen_marker = user
                    break
        m.TestMatch(id=m.new_random_slug(m.TestMatch), test=chosen_test, solution=sol,
                    coursework=coursework, initiator=initiator, waiting_to_run=True,
                    visible_to_developer=visible, marker=chosen_marker).save()
        unassigned_tests.remove(chosen_test)
        unassigned_users.remove(chosen_marker)
