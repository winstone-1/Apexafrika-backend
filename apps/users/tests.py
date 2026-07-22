from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            gamer_tag="TestGamer",
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.gamer_tag, "TestGamer")
        self.assertEqual(self.user.role, User.Role.PLAYER)

    def test_user_str_method(self):
        self.assertEqual(str(self.user), "testuser (TestGamer)")

    def test_win_rate_update(self):
        self.user.total_matches = 10
        self.user.tournaments_won = 7
        self.user.update_win_rate()
        self.assertEqual(self.user.win_rate, 70.0)
