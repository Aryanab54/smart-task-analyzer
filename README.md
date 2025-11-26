# Smart Task Analyzer

A mini-application that intelligently scores and prioritizes tasks based on multiple factors including urgency, importance, effort, and dependencies.

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run database migrations:
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

4. Start the Django development server:
```bash
python3 manage.py runserver
```

The API will be available at `http://localhost:8000/api/tasks/`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Open `index.html` in a web browser or serve it using a simple HTTP server:
```bash
python3 -m http.server 3000
```

Then visit `http://localhost:3000`

### Running Tests

To run the unit tests for the scoring algorithm:
```bash
cd backend
python3 manage.py test task_manager.tests
```

## Algorithm Explanation

The Smart Task Analyzer uses a multi-factor scoring algorithm that considers four key dimensions:

### 1. Urgency Score (0.0 - 1.0)
- **Past due tasks**: 1.0 (maximum urgency)
- **Due today**: 0.9
- **Due within 3 days**: 0.8
- **Due within 7 days**: 0.6
- **Due within 14 days**: 0.4
- **Further out**: Decreasing score based on days until due

### 2. Importance Score (0.1 - 1.0)
- Direct mapping from user-provided importance rating (1-10 scale)
- Normalized to 0.1-1.0 range

### 3. Effort Score (0.4 - 1.0)
- **≤ 1 hour**: 1.0 (quick wins)
- **≤ 4 hours**: 0.8
- **≤ 8 hours**: 0.6
- **> 8 hours**: 0.4

### 4. Dependency Score (0.5 - 1.0)
- **No dependencies**: 0.5 (baseline)
- **With dependencies**: 0.5 + (0.1 × number of dependencies)
- Tasks that block others get higher priority

### Scoring Strategies

The algorithm supports four different prioritization strategies:

1. **Smart Balance** (Default): Balanced weighting of all factors
   - Urgency: 30%, Importance: 30%, Effort: 20%, Dependencies: 20%

2. **Fastest Wins**: Prioritizes low-effort tasks for quick completion
   - Effort: 70%, Importance: 30%

3. **High Impact**: Focuses on importance above all else
   - Importance: 80%, Urgency: 20%

4. **Deadline Driven**: Prioritizes based on due dates
   - Urgency: 80%, Importance: 20%

### Edge Case Handling

- **Invalid dates**: Default to medium urgency (0.5)
- **Missing data**: Graceful degradation with sensible defaults
- **Circular dependencies**: Detected and rejected with error message
- **Out-of-range values**: Validated and clamped to acceptable ranges

## Design Decisions

### Backend Architecture
- **Django REST Framework**: Chosen for rapid API development and built-in serialization
- **Modular scoring system**: Separate `TaskScorer` class allows easy strategy switching
- **Real-time algorithm**: Task suggestions use dynamic scoring, not static data
- **In-memory storage**: Tasks analyzed via `/analyze/` are stored for personalized suggestions
- **Comprehensive validation**: Input validation at multiple levels

### Frontend Architecture
- **Vanilla JavaScript**: No framework dependencies for simplicity
- **Class-based organization**: Clean separation of concerns
- **Dual input methods**: Manual form for simple tasks, bulk JSON for complex scenarios
- **Visual priority indicators**: Color-coded results (Red: High ≥0.7, Orange: Medium 0.5-0.69, Green: Low <0.5)
- **Responsive design**: Works on desktop and mobile devices
- **Progressive enhancement**: Graceful error handling and loading states

### Algorithm Design
- **Configurable strategies**: Users can choose different prioritization approaches
- **Normalized scoring**: All factors scaled to 0-1 range for consistent weighting
- **Dependency awareness**: Considers task interdependencies in scoring
- **Time-sensitive**: Accounts for current date in urgency calculations

## Features

### Core Functionality
- **Multi-factor Priority Scoring**: Considers urgency, importance, effort, and dependencies
- **4 Sorting Strategies**: Smart Balance, Fastest Wins, High Impact, Deadline Driven
- **Real-time Suggestions**: Dynamic task recommendations based on current analysis
- **Dependency Management**: Handles task interdependencies with circular dependency detection
- **Visual Priority Coding**: Color-coded results for quick task identification

### Input Methods
- **Manual Form**: Simple task entry with title, due date, hours, and importance
- **Bulk JSON**: Advanced input supporting dependencies and multiple tasks
- **Task Storage**: Analyzed tasks are stored for personalized suggestions

## Time Breakdown

- **Algorithm Design & Implementation**: 45 minutes
- **Backend Development (Django/API)**: 60 minutes
- **Frontend Development**: 75 minutes
- **Real Algorithm Implementation**: 30 minutes
- **Testing & Validation**: 30 minutes
- **Documentation & Polish**: 30 minutes
- **Total**: ~4.5 hours

## API Endpoints

### POST /api/tasks/analyze/
Analyzes and sorts a list of tasks by priority score.

**Request Body:**
```json
{
  "tasks": [
    {
      "title": "Fix login bug",
      "due_date": "2025-01-30",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": []
    }
  ],
  "strategy": "smart_balance"
}
```

**Response:**
```json
{
  "tasks": [
    {
      "title": "Fix login bug",
      "due_date": "2025-01-30",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": [],
      "priority_score": 0.725,
      "explanation": "High importance • Quick completion"
    }
  ]
}
```

### GET /api/tasks/suggest/
Returns the top 3 recommended tasks with explanations using real-time priority scoring.

**Response:**
```json
{
  "suggested_tasks": [
    {
      "title": "Fix critical login bug",
      "due_date": "2025-01-15",
      "estimated_hours": 2,
      "importance": 9,
      "dependencies": [],
      "priority_score": 0.83,
      "explanation": "High importance • Quick completion"
    }
  ]
}
```

### POST /api/tasks/add/
Adds a single task to the suggestion pool for personalized recommendations.

**Request Body:**
```json
{
  "title": "New urgent task",
  "due_date": "2025-01-10",
  "estimated_hours": 1,
  "importance": 10
}
```

## Future Improvements

Given more time, I would implement:

1. **User Preferences**: Customizable weighting for scoring factors
2. **Task Dependencies**: Visual dependency graph with cycle detection
3. **Calendar Integration**: Consider weekends/holidays in urgency calculation
4. **Machine Learning**: Learn from user feedback to improve recommendations
5. **Collaboration Features**: Team task management and assignment
6. **Advanced Analytics**: Task completion patterns and productivity insights
7. **Mobile App**: Native mobile application for on-the-go task management
8. **Integration APIs**: Connect with popular task management tools

## Technical Considerations

- **Scalability**: Current algorithm is O(n) for scoring, O(n²) for dependency checking
- **Performance**: Suitable for hundreds of tasks; would need optimization for thousands
- **Security**: Input validation prevents injection attacks; would add authentication for production
- **Accessibility**: Frontend follows basic accessibility guidelines; could be enhanced further