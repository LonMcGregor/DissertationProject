
import feedback.models as m


def user_is_member_of_test_match_feedback_group(user, test_match_instance):
    """Return whether or not a user is a member of the
    feedback group for a given test match"""
    feedback_ftm = m.FeedbackForTestMatch.objects.filter(test_match=test_match_instance)
    if not feedback_ftm.exists():
        return False
    feedback_group = feedback_ftm.first().group
    return m.FeedbackMembership.objects.filter(group=feedback_group, user=user).exists()


def is_submission_written_by_peer_in_testing_group(user, submission):
    """Assuming there is a feedback group for the creator of @submission
    that the @user is trying to view, determine if this group in the
    coursework also includes @user"""
    if user == submission.creator:
        return True
    submission_groups = [member.group for member in
                         m.FeedbackMembership.objects.filter(user=submission.creator)]
    user_groups = [member.group for member in m.FeedbackMembership.objects.filter(user=user)]
    common = list(set(submission_groups).intersection(user_groups))
    for group in common:
        if m.FeedbackPlan.objects.filter(group=group, coursework=submission.coursework).exists():
            return True
    return False
