from django.test import TestCase
from datetime import date, timedelta
from .scoring import TaskScorer


class TaskScorerTestCase(TestCase):
    def setUp(self):
        self.scorer = TaskScorer()
        self.sample_task = {
            'title': 'Test Task',
            'due_date': (date.today() + timedelta(days=3)).isoformat(),
            'estimated_hours': 2,
            'importance': 7,
            'dependencies': []
        }
    
    def test_urgency_calculation_past_due(self):
        """Test urgency calculation for past due tasks"""
        past_date = (date.today() - timedelta(days=1)).isoformat()
        urgency = self.scorer._calculate_urgency(past_date)
        self.assertEqual(urgency, 1.0)
    
    def test_urgency_calculation_due_today(self):
        """Test urgency calculation for tasks due today"""
        today = date.today().isoformat()
        urgency = self.scorer._calculate_urgency(today)
        self.assertEqual(urgency, 0.9)
    
    def test_effort_score_calculation(self):
        """Test effort score calculation"""
        # Quick task (1 hour)
        quick_score = self.scorer._calculate_effort_score(1)
        self.assertEqual(quick_score, 1.0)
        
        # Long task (10 hours)
        long_score = self.scorer._calculate_effort_score(10)
        self.assertEqual(long_score, 0.4)
    
    def test_dependency_score_calculation(self):
        """Test dependency score calculation"""
        # No dependencies
        no_deps = self.scorer._calculate_dependency_score([])
        self.assertEqual(no_deps, 0.5)
        
        # Multiple dependencies
        with_deps = self.scorer._calculate_dependency_score([1, 2, 3])
        self.assertGreater(with_deps, 0.5)
    
    def test_circular_dependency_detection(self):
        """Test circular dependency detection"""
        tasks_with_cycle = [
            {'id': 1, 'dependencies': [2]},
            {'id': 2, 'dependencies': [3]},
            {'id': 3, 'dependencies': [1]}
        ]
        
        tasks_without_cycle = [
            {'id': 1, 'dependencies': [2]},
            {'id': 2, 'dependencies': [3]},
            {'id': 3, 'dependencies': []}
        ]
        
        self.assertTrue(self.scorer.detect_circular_dependencies(tasks_with_cycle))
        self.assertFalse(self.scorer.detect_circular_dependencies(tasks_without_cycle))
    
    def test_different_strategies(self):
        """Test different scoring strategies"""
        strategies = ['smart_balance', 'fastest_wins', 'high_impact', 'deadline_driven']
        
        for strategy in strategies:
            scorer = TaskScorer(strategy)
            score = scorer.calculate_priority_score(self.sample_task)
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 1)