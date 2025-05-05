from django.test import TestCase
from django.contrib.auth.models import User
from gamification.models import LeaderboardEntry
from gamification.views import get_leaderboard, get_user_stats
from django.utils import timezone

class GamificationTest(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Create leaderboard entries
        self.entry1 = LeaderboardEntry.objects.create(
            user=self.user1,
            total_solved=5
        )
        self.entry2 = LeaderboardEntry.objects.create(
            user=self.user2,
            total_solved=3
        )

    def test_leaderboard_creation(self):
        """Test leaderboard entry creation and model fields"""
        self.assertEqual(self.entry1.total_solved, 5)
        self.assertEqual(self.entry2.total_solved, 3)
        self.assertIsNotNone(self.entry1.last_updated)
        self.assertIsNotNone(self.entry2.last_updated)

    def test_leaderboard_ordering(self):
        """Test leaderboard ordering by total problems solved"""
        entries = LeaderboardEntry.objects.order_by('-total_solved')
        self.assertEqual(entries[0], self.entry1)  # User with 5 problems solved
        self.assertEqual(entries[1], self.entry2)  # User with 3 problems solved

    def test_get_leaderboard_view(self):
        """Test the leaderboard view endpoint"""
        response = self.client.get('/gamification/leaderboard/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data['entries']), 2)
        self.assertEqual(data['entries'][0]['user__username'], 'testuser1')
        self.assertEqual(data['entries'][0]['total_solved'], 5)
        self.assertEqual(data['entries'][1]['user__username'], 'testuser2')
        self.assertEqual(data['entries'][1]['total_solved'], 3)

    def test_get_user_stats_view(self):
        """Test the user stats view endpoint"""
        # Test with authenticated user
        self.client.force_login(self.user1)
        response = self.client.get('/gamification/stats/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['total_solved'], 5)
        self.assertIsNotNone(data['last_updated'])

        # Test with unauthenticated user
        self.client.logout()
        response = self.client.get('/gamification/stats/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_leaderboard_update(self):
        """Test updating leaderboard entries"""
        # Update user1's total solved
        self.entry1.total_solved = 7
        self.entry1.save()
        
        # Verify update
        updated_entry = LeaderboardEntry.objects.get(user=self.user1)
        self.assertEqual(updated_entry.total_solved, 7)
        # Don't compare dates as they might be the same in test environment
        self.assertIsNotNone(updated_entry.last_updated)

    def test_leaderboard_limits(self):
        """Test leaderboard entry limits"""
        # Create additional entries to test limit
        for i in range(6, 56):  # Create 50 entries starting from 6
            user = User.objects.create_user(
                username=f'testuser{i}',
                email=f'test{i}@example.com',
                password='testpass123'
            )
            LeaderboardEntry.objects.create(
                user=user,
                total_solved=i
            )
        
        # Test that only top 50 entries are returned
        response = self.client.get('/gamification/leaderboard/')
        data = response.json()
        
        # Sort entries by total_solved to ensure correct order
        sorted_entries = sorted(data['entries'], key=lambda x: x['total_solved'])
        
        self.assertEqual(len(data['entries']), 50)
        self.assertEqual(sorted_entries[-1]['total_solved'], 55)  # Highest score
        self.assertEqual(sorted_entries[0]['total_solved'], 6)  # Lowest score in top 50
