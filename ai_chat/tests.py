from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import Profile
from problems.models import Problem
from ai_chat.views import get_problem_type_prompt, get_experience_guidance
import json
import os

class AIChatTest(TestCase):
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
        
        # Create test problem
        self.problem = Problem.objects.create(
            name="Test Problem",
            language="python",
            difficulty="easy",
            description="Test description",
            test_cases={},
            boilerplate_code="def solution(): pass",
            problem_type="python_basics",
            order=1
        )

    def test_get_problem_type_prompt(self):
        """Test problem type specific prompt generation"""
        # Test with valid problem type
        prompt = get_problem_type_prompt(self.problem.id)
        self.assertIn("Python basics", prompt)
        self.assertIn("basic concepts", prompt)
        
        # Test with invalid problem ID
        prompt = get_problem_type_prompt(999)
        self.assertEqual(prompt, "")
        
        # Test with problem type not in prompts
        self.problem.problem_type = "unknown_type"
        self.problem.save()
        prompt = get_problem_type_prompt(self.problem.id)
        self.assertEqual(prompt, "")

    def test_get_experience_guidance(self):
        """Test experience level specific guidance"""
        # Test beginner guidance
        guidance = get_experience_guidance("beginner")
        self.assertIn("basic programming concepts", guidance)
        self.assertIn("simple, non-technical language", guidance)
        
        # Test intermediate guidance
        guidance = get_experience_guidance("intermediate")
        self.assertIn("code structure", guidance)
        self.assertIn("optimization techniques", guidance)
        
        # Test advanced guidance
        guidance = get_experience_guidance("advanced")
        self.assertIn("high-level design patterns", guidance)
        self.assertIn("performance optimization", guidance)
        
        # Test invalid experience level
        guidance = get_experience_guidance("invalid")
        self.assertEqual(guidance, "")

    def test_prompt_building_blocks(self):
        """Test the prompt building blocks JSON files"""
        # Test problem type prompts
        with open(os.path.join(os.path.dirname(__file__), 'prompt_building_blocks', 'problem_type_prompts.json'), 'r') as f:
            problem_prompts = json.load(f)
            self.assertIn("python_basics", problem_prompts)
            self.assertIn("hint_guidance", problem_prompts["python_basics"])
            self.assertIn("additional_context", problem_prompts["python_basics"])
        
        # Test experience guidance
        with open(os.path.join(os.path.dirname(__file__), 'prompt_building_blocks', 'experience_guidance.json'), 'r') as f:
            experience_guidance = json.load(f)
            self.assertIn("beginner", experience_guidance)
            self.assertIn("intermediate", experience_guidance)
            self.assertIn("advanced", experience_guidance)
            for level in ["beginner", "intermediate", "advanced"]:
                self.assertIn("guidance", experience_guidance[level])
                self.assertIn("context", experience_guidance[level])
