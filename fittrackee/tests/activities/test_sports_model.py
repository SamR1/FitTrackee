from typing import Dict, Optional

from fittrackee.activities.models import Activity, Sport
from fittrackee.users.models import User
from flask import Flask


class TestSportModel:
    @staticmethod
    def assert_sport_model(
        sport: Sport, is_admin: Optional[bool] = False
    ) -> Dict:
        assert 1 == sport.id
        assert 'Cycling' == sport.label
        assert '<Sport \'Cycling\'>' == str(sport)

        serialized_sport = sport.serialize(is_admin)
        assert 1 == serialized_sport['id']
        assert 'Cycling' == serialized_sport['label']
        assert serialized_sport['is_active'] is True
        return serialized_sport

    def test_sport_model(self, app: Flask, sport_1_cycling: Sport) -> None:
        serialized_sport = self.assert_sport_model(sport_1_cycling)
        assert 'has_activities' not in serialized_sport

    def test_sport_model_with_activity(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        activity_cycling_user_1: Activity,
    ) -> None:
        serialized_sport = self.assert_sport_model(sport_1_cycling)
        assert 'has_activities' not in serialized_sport

    def test_sport_model_with_activity_as_admin(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        activity_cycling_user_1: Activity,
    ) -> None:
        serialized_sport = self.assert_sport_model(sport_1_cycling, True)
        assert serialized_sport['has_activities'] is True
