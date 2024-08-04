from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.reports.models import Report
from fittrackee.reports.reports_service import ReportService
from fittrackee.tests.comments.mixins import CommentMixin
from fittrackee.users.models import User
from fittrackee.workouts.models import Workout


class ReportServiceCreateAdminActionMixin(CommentMixin):
    def create_report_for_user(
        self,
        report_service: ReportService,
        reporter: User,
        reported_user: User,
    ) -> Report:
        report = report_service.create_report(
            reporter=reporter,
            object_id=reported_user.username,
            object_type="user",
            note=self.random_string(),
        )
        return report

    def create_report_for_comment(
        self,
        report_service: ReportService,
        reporter: User,
        commenter: User,
        workout: Workout,
    ) -> Report:
        workout.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            commenter,
            workout,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        report = report_service.create_report(
            reporter=reporter,
            object_id=comment.short_id,
            object_type="comment",
            note=self.random_string(),
        )
        return report

    def create_report_for_workout(
        self,
        report_service: ReportService,
        reporter: User,
        workout: Workout,
    ) -> Report:
        workout.workout_visibility = PrivacyLevel.PUBLIC
        report = report_service.create_report(
            reporter=reporter,
            object_id=workout.short_id,
            object_type="workout",
            note=self.random_string(),
        )
        return report
