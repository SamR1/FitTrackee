from fittrackee import db
from fittrackee.administration.models import AdminAction
from fittrackee.users.models import User
from fittrackee.workouts.models import Workout


class WorkoutMixin:
    @staticmethod
    def create_admin_workout_suspension_action(
        admin: User, user: User, workout: Workout
    ) -> AdminAction:
        admin_action = AdminAction(
            action_type="workout_suspension",
            admin_user_id=admin.id,
            workout_id=workout.id,
            user_id=user.id,
        )
        db.session.add(admin_action)
        return admin_action
