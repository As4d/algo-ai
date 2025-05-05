from django.test import TestCase
from django.contrib.auth.models import User
from problems.models import Problem
from accounts.models import Profile
from code_execution.views import (
    create_execution_environment,
    run_code_with_test,
    compare_outputs,
    update_leaderboard,
    update_user_progress,
    create_submission,
    update_streak
)
from datetime import datetime, timedelta
from django.utils import timezone

class CodeExecutionTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test profile
        self.profile = Profile.objects.create(
            user=self.user,
            experience_level='beginner',
            description='Test profile',
            streak=0,
            high_score_streak=0
        )
        
        # Create test problem
        self.problem = Problem.objects.create(
            name="Test Problem",
            language="python",
            difficulty="easy",
            description="Test description",
            test_cases={
                "test1": {"input": "5", "output": "Hello, World!"},
                "test2": {"input": "10", "output": "Hello, World!"}
            },
            boilerplate_code="def solution(): pass",
            problem_type="algorithm",
            order=1
        )

    def test_create_execution_environment(self):
        """Test the creation of a safe execution environment"""
        # Test basic environment creation
        env = create_execution_environment()
        self.assertIn("print", env)
        self.assertNotIn("__import__", env)
        self.assertNotIn("eval", env)
        
        # Test environment with input handling
        env_with_input = create_execution_environment("test input")
        self.assertIn("input", env_with_input)
        self.assertEqual(env_with_input["input"](""), "test input")

    def test_run_code_with_test(self):
        """Test code execution with various scenarios"""
        # Test successful code execution
        test_code = "print('Hello, World!')"
        result = run_code_with_test(test_code)
        self.assertTrue(result["success"])
        self.assertEqual(result["output"], "Hello, World!")

        # Test code with input
        test_code = "x = input(); print(f'Hello, {x}!')"
        result = run_code_with_test(test_code, "World")
        self.assertTrue(result["success"])
        self.assertEqual(result["output"], "Hello, World!")

        # Test syntax error
        test_code = "print('Hello, World!'"  # Missing closing parenthesis
        result = run_code_with_test(test_code)
        self.assertFalse(result["success"])
        self.assertIn("SyntaxError", result["error"])

        # Test runtime error
        test_code = "1/0"  # Division by zero
        result = run_code_with_test(test_code)
        self.assertFalse(result["success"])
        self.assertIn("ZeroDivisionError", result["error"])

        # Test timeout
        test_code = "while True: pass"  # Infinite loop
        result = run_code_with_test(test_code)
        self.assertFalse(result["success"])
        self.assertIn("timed out", result["error"])

    def test_compare_outputs(self):
        """Test output comparison functionality"""
        # Test exact match
        self.assertTrue(compare_outputs("Hello", "Hello"))
        
        # Test with different whitespace
        self.assertTrue(compare_outputs("Hello\nWorld", "Hello\nWorld"))
        self.assertTrue(compare_outputs("Hello\r\nWorld", "Hello\nWorld"))
        
        # Test non-matching outputs
        self.assertFalse(compare_outputs("Hello", "World"))

    def test_update_leaderboard(self):
        """Test leaderboard update functionality"""
        # Test first completion
        entry = update_leaderboard(self.user, self.problem, False)
        self.assertEqual(entry.total_solved, 1)
        
        # Test subsequent completion of same problem
        entry = update_leaderboard(self.user, self.problem, True)
        self.assertEqual(entry.total_solved, 1)  # Should not increment
        
        # Test completion of different problem
        new_problem = Problem.objects.create(
            name="New Problem",
            language="python",
            difficulty="easy",
            description="New description",
            test_cases={},
            boilerplate_code="",
            problem_type="algorithm",
            order=2
        )
        entry = update_leaderboard(self.user, new_problem, False)
        self.assertEqual(entry.total_solved, 2)

    def test_update_user_progress(self):
        """Test user progress tracking"""
        # Test first attempt
        progress = update_user_progress(self.user, self.problem, 60, False)
        self.assertEqual(progress.attempts, 1)
        self.assertEqual(progress.time_spent, 60)
        self.assertFalse(progress.is_completed)
        
        # Test successful completion
        progress = update_user_progress(self.user, self.problem, 120, True)
        self.assertEqual(progress.attempts, 2)
        self.assertEqual(progress.time_spent, 120)
        self.assertTrue(progress.is_completed)

    def test_create_submission(self):
        """Test submission creation"""
        # Test successful submission
        submission = create_submission(
            self.user,
            self.problem,
            "print('Hello, World!')",
            True
        )
        self.assertEqual(submission.status, "completed")
        self.assertEqual(submission.language, "python")
        
        # Test failed submission
        submission = create_submission(
            self.user,
            self.problem,
            "print('Hello, World!'",  # Syntax error
            False
        )
        self.assertEqual(submission.status, "attempted")

    def test_update_streak(self):
        """Test streak tracking functionality"""
        # Test first problem solved
        self.profile.last_solved_date = None  # Simulate first problem solve
        self.profile.save()
        update_streak(self.user)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.streak, 1)
        self.assertEqual(self.profile.high_score_streak, 1)
        
        # Test consecutive day streak
        self.profile.last_solved_date = timezone.now().date() - timedelta(days=1)
        self.profile.save()
        update_streak(self.user)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.streak, 2)
        self.assertEqual(self.profile.high_score_streak, 2)
        
        # Test streak reset
        self.profile.last_solved_date = timezone.now().date() - timedelta(days=2)
        self.profile.save()
        update_streak(self.user)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.streak, 1)
        self.assertEqual(self.profile.high_score_streak, 2)  # High score should remain
