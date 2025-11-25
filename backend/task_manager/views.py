from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .scoring import TaskScorer
from .serializers import TaskAnalysisSerializer, TaskWithScoreSerializer


@api_view(['POST'])
def analyze_tasks(request):
    """Analyze and sort tasks by priority score"""
    serializer = TaskAnalysisSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    tasks = serializer.validated_data['tasks']
    strategy = serializer.validated_data.get('strategy', 'smart_balance')
    
    scorer = TaskScorer(strategy)
    
    # Check for circular dependencies
    if scorer.detect_circular_dependencies(tasks):
        return Response(
            {'error': 'Circular dependencies detected in task list'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Calculate scores and add explanations
    scored_tasks = []
    for task in tasks:
        try:
            score = scorer.calculate_priority_score(task)
            explanation = _generate_explanation(task, score, strategy)
            
            scored_task = {
                **task,
                'priority_score': round(score, 3),
                'explanation': explanation
            }
            scored_tasks.append(scored_task)
        except Exception as e:
            return Response(
                {'error': f'Error processing task "{task.get("title", "Unknown")}": {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Sort by priority score (highest first)
    scored_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return Response({'tasks': scored_tasks})


@api_view(['GET'])
def suggest_tasks(request):
    """Get top 3 task suggestions with explanations"""
    # For demo purposes, return sample suggestions
    # In a real app, this would analyze user's actual tasks
    sample_tasks = [
        {
            'title': 'Fix critical login bug',
            'due_date': '2025-01-15',
            'estimated_hours': 2,
            'importance': 9,
            'dependencies': [],
            'priority_score': 0.85,
            'explanation': 'High importance task with moderate urgency - critical for user experience'
        },
        {
            'title': 'Update documentation',
            'due_date': '2025-01-20',
            'estimated_hours': 1,
            'importance': 6,
            'dependencies': [],
            'priority_score': 0.72,
            'explanation': 'Quick win task that can be completed efficiently'
        },
        {
            'title': 'Implement new feature',
            'due_date': '2025-01-25',
            'estimated_hours': 8,
            'importance': 8,
            'dependencies': [],
            'priority_score': 0.68,
            'explanation': 'Important feature but requires significant time investment'
        }
    ]
    
    return Response({'suggested_tasks': sample_tasks[:3]})


def _generate_explanation(task, score, strategy):
    """Generate explanation for why task received its score"""
    explanations = []
    
    if strategy == 'fastest_wins':
        if task['estimated_hours'] <= 2:
            explanations.append('Quick win - low effort required')
        explanations.append(f'Importance level: {task["importance"]}/10')
    
    elif strategy == 'high_impact':
        explanations.append(f'High importance ({task["importance"]}/10)')
        if score > 0.8:
            explanations.append('Critical priority task')
    
    elif strategy == 'deadline_driven':
        explanations.append(f'Due date: {task["due_date"]}')
        if score > 0.8:
            explanations.append('Urgent deadline approaching')
    
    else:  # smart_balance
        if task['importance'] >= 8:
            explanations.append('High importance')
        if task['estimated_hours'] <= 2:
            explanations.append('Quick completion')
        if task.get('dependencies'):
            explanations.append('Blocks other tasks')
    
    return ' • '.join(explanations) if explanations else 'Balanced priority scoring'