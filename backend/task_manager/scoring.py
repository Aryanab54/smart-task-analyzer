from datetime import date, timedelta
import math


class TaskScorer:
    def __init__(self, strategy='smart_balance'):
        self.strategy = strategy
    
    def calculate_priority_score(self, task_data):
        """Calculate priority score based on multiple factors"""
        urgency_score = self._calculate_urgency(task_data['due_date'])
        importance_score = task_data['importance'] / 10.0
        effort_score = self._calculate_effort_score(task_data['estimated_hours'])
        dependency_score = self._calculate_dependency_score(task_data.get('dependencies', []))
        
        if self.strategy == 'fastest_wins':
            return effort_score * 0.7 + importance_score * 0.3
        elif self.strategy == 'high_impact':
            return importance_score * 0.8 + urgency_score * 0.2
        elif self.strategy == 'deadline_driven':
            return urgency_score * 0.8 + importance_score * 0.2
        else:  # smart_balance
            return (urgency_score * 0.3 + importance_score * 0.3 + 
                   effort_score * 0.2 + dependency_score * 0.2)
    
    def _calculate_urgency(self, due_date_str):
        """Calculate urgency based on due date"""
        try:
            due_date = date.fromisoformat(due_date_str)
            today = date.today()
            days_until_due = (due_date - today).days
            
            if days_until_due < 0:  # Past due
                return 1.0
            elif days_until_due == 0:  # Due today
                return 0.9
            elif days_until_due <= 3:  # Due within 3 days
                return 0.8
            elif days_until_due <= 7:  # Due within a week
                return 0.6
            elif days_until_due <= 14:  # Due within 2 weeks
                return 0.4
            else:
                return max(0.1, 1.0 / (days_until_due / 7))
        except:
            return 0.5  # Default if date parsing fails
    
    def _calculate_effort_score(self, estimated_hours):
        """Calculate effort score (lower effort = higher score for quick wins)"""
        if estimated_hours <= 1:
            return 1.0
        elif estimated_hours <= 4:
            return 0.8
        elif estimated_hours <= 8:
            return 0.6
        else:
            return 0.4
    
    def _calculate_dependency_score(self, dependencies):
        """Calculate dependency score (fewer dependencies = higher priority)"""
        if not dependencies:
            return 1.0  # No dependencies = can start immediately
        # More dependencies = lower priority (harder to start)
        return max(0.3, 1.0 - (len(dependencies) * 0.15))
    
    def detect_circular_dependencies(self, tasks):
        """Detect circular dependencies in task list"""
        task_map = {task.get('id', i): task for i, task in enumerate(tasks)}
        
        def has_cycle(task_id, visited, rec_stack):
            visited.add(task_id)
            rec_stack.add(task_id)
            
            task = task_map.get(task_id)
            if task:
                for dep_id in task.get('dependencies', []):
                    if dep_id not in visited:
                        if has_cycle(dep_id, visited, rec_stack):
                            return True
                    elif dep_id in rec_stack:
                        return True
            
            rec_stack.remove(task_id)
            return False
        
        visited = set()
        for task_id in task_map.keys():
            if task_id not in visited:
                if has_cycle(task_id, visited, set()):
                    return True
        return False