from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .scoring import TaskScorer
from .serializers import TaskAnalysisSerializer, TaskWithScoreSerializer, TaskSerializer


@api_view(['POST'])
def analyze_tasks(request):
    """Analyze and sort tasks by priority score"""
    global SUGGESTION_TASKS
    
    serializer = TaskAnalysisSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    tasks = serializer.validated_data['tasks']
    strategy = serializer.validated_data.get('strategy', 'smart_balance')
    
    # Store tasks for suggestions (in-memory)
    SUGGESTION_TASKS = tasks.copy()
    
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


# In-memory task storage for suggestions
SUGGESTION_TASKS = []

@api_view(['GET'])
def suggest_tasks(request):
    """Get top 3 task suggestions with explanations using real algorithm"""
    global SUGGESTION_TASKS
    
    # If no tasks stored, return default suggestions
    if not SUGGESTION_TASKS:
        default_tasks = [
            {
                'title': 'Fix critical login bug',
                'due_date': '2025-01-15',
                'estimated_hours': 2,
                'importance': 9,
                'dependencies': []
            },
            {
                'title': 'Update documentation', 
                'due_date': '2025-01-20',
                'estimated_hours': 1,
                'importance': 6,
                'dependencies': []
            },
            {
                'title': 'Implement new feature',
                'due_date': '2025-01-25', 
                'estimated_hours': 8,
                'importance': 8,
                'dependencies': []
            },
            {
                'title': 'Code review',
                'due_date': '2025-01-12',
                'estimated_hours': 3,
                'importance': 7,
                'dependencies': []
            },
            {
                'title': 'Deploy to staging',
                'due_date': '2025-01-18',
                'estimated_hours': 2,
                'importance': 8,
                'dependencies': []
            }
        ]
        SUGGESTION_TASKS = default_tasks
    
    # Apply real scoring algorithm
    scorer = TaskScorer('smart_balance')
    scored_tasks = []
    
    for task in SUGGESTION_TASKS:
        try:
            score = scorer.calculate_priority_score(task)
            explanation = _generate_explanation(task, score, 'smart_balance')
            
            scored_task = {
                **task,
                'priority_score': round(score, 3),
                'explanation': explanation
            }
            scored_tasks.append(scored_task)
        except Exception:
            continue
    
    # Sort by priority score and return top 3
    scored_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return Response({'suggested_tasks': scored_tasks[:3]})


@api_view(['POST'])
def add_task_to_suggestions(request):
    """Add a single task to the suggestion pool"""
    global SUGGESTION_TASKS
    
    # Validate task data
    required_fields = ['title', 'due_date', 'estimated_hours', 'importance']
    task_data = request.data
    
    for field in required_fields:
        if field not in task_data:
            return Response(
                {'error': f'Missing required field: {field}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Add dependencies if not provided
    if 'dependencies' not in task_data:
        task_data['dependencies'] = []
    
    # Add to suggestion pool
    SUGGESTION_TASKS.append(task_data)
    
    return Response({
        'message': 'Task added to suggestion pool',
        'task': task_data,
        'total_tasks': len(SUGGESTION_TASKS)
    })


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