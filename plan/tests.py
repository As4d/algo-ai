from django.test import TestCase
from django.contrib.auth.models import User
from problems.models import Problem
from accounts.models import Profile
from plan.models import Plan, PlanProblem
from plan.views import create_plan, list_plans, get_plan_details
from django.utils import timezone
import json

class PlanTest(TestCase):
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
            description='Test profile'
        )
        
        # Create test problems
        self.problem1 = Problem.objects.create(
            name="Test Problem 1",
            language="python",
            difficulty="easy",
            description="Test description 1",
            test_cases={},
            boilerplate_code="def solution(): pass",
            problem_type="python_basics",
            order=1
        )
        self.problem2 = Problem.objects.create(
            name="Test Problem 2",
            language="python",
            difficulty="intermediate",
            description="Test description 2",
            test_cases={},
            boilerplate_code="def solution(): pass",
            problem_type="algorithm",
            order=2
        )

    def test_plan_creation(self):
        """Test plan creation and model fields"""
        plan = Plan.objects.create(
            user=self.user,
            name="Test Plan",
            description="Test plan description",
            duration_days=7,
            difficulty="beginner",
            problem_types=["python_basics", "algorithm"]
        )
        
        self.assertEqual(plan.name, "Test Plan")
        self.assertEqual(plan.duration_days, 7)
        self.assertEqual(plan.difficulty, "beginner")
        self.assertEqual(plan.problem_types, ["python_basics", "algorithm"])
        self.assertTrue(plan.is_active)

    def test_plan_problem_creation(self):
        """Test plan problem creation and ordering"""
        plan = Plan.objects.create(
            user=self.user,
            name="Test Plan",
            description="Test plan description",
            duration_days=7,
            difficulty="beginner",
            problem_types=["python_basics", "algorithm"]
        )
        
        # Create plan problems
        plan_problem1 = PlanProblem.objects.create(
            plan=plan,
            problem=self.problem1,
            order=1
        )
        plan_problem2 = PlanProblem.objects.create(
            plan=plan,
            problem=self.problem2,
            order=2
        )
        
        # Test ordering
        problems = PlanProblem.objects.filter(plan=plan).order_by('order')
        self.assertEqual(problems[0], plan_problem1)
        self.assertEqual(problems[1], plan_problem2)
        
        # Test problem completion
        plan_problem1.is_completed = True
        plan_problem1.completed_at = timezone.now()
        plan_problem1.save()
        
        completed_problems = PlanProblem.objects.filter(plan=plan, is_completed=True)
        self.assertEqual(completed_problems.count(), 1)
        self.assertEqual(completed_problems[0], plan_problem1)

    def test_list_plans_view(self):
        """Test the list plans view endpoint"""
        # Create a test plan
        plan = Plan.objects.create(
            user=self.user,
            name="Test Plan",
            description="Test plan description",
            duration_days=7,
            difficulty="beginner",
            problem_types=["python_basics", "algorithm"]
        )
        
        # Add problems to plan
        PlanProblem.objects.create(plan=plan, problem=self.problem1, order=1)
        PlanProblem.objects.create(plan=plan, problem=self.problem2, order=2)
        
        # Test the view
        self.client.force_login(self.user)
        response = self.client.get('/plan/list/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Test Plan")
        self.assertEqual(data[0]['progress']['total'], 2)
        self.assertEqual(data[0]['progress']['completed'], 0)
        self.assertEqual(data[0]['progress']['percentage'], 0)

    def test_get_plan_details_view(self):
        """Test the get plan details view endpoint"""
        # Create a test plan
        plan = Plan.objects.create(
            user=self.user,
            name="Test Plan",
            description="Test plan description",
            duration_days=7,
            difficulty="beginner",
            problem_types=["python_basics", "algorithm"]
        )
        
        # Add problems to plan
        PlanProblem.objects.create(plan=plan, problem=self.problem1, order=1)
        PlanProblem.objects.create(plan=plan, problem=self.problem2, order=2)
        
        # Test the view
        self.client.force_login(self.user)
        response = self.client.get(f'/plan/{plan.id}/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['name'], "Test Plan")
        self.assertEqual(len(data['problems']), 2)
        self.assertEqual(data['problems'][0]['name'], "Test Problem 1")
        self.assertEqual(data['problems'][1]['name'], "Test Problem 2")
        self.assertEqual(data['progress']['total'], 2)
        self.assertEqual(data['progress']['completed'], 0)
        self.assertEqual(data['progress']['percentage'], 0)
