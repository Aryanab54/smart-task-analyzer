class TaskAnalyzer {
    constructor() {
        this.tasks = [];
        this.apiBase = 'http://localhost:8000/api/tasks';
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // Form submission
        document.getElementById('task-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addTask();
        });

        // Analyze button
        document.getElementById('analyze-btn').addEventListener('click', () => {
            this.analyzeTasks();
        });

        // Suggestions button
        document.getElementById('get-suggestions').addEventListener('click', () => {
            this.getSuggestions();
        });
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }

    addTask() {
        const form = document.getElementById('task-form');
        const formData = new FormData(form);
        
        const task = {
            title: formData.get('title') || document.getElementById('title').value,
            due_date: formData.get('due_date') || document.getElementById('due_date').value,
            estimated_hours: parseFloat(formData.get('estimated_hours') || document.getElementById('estimated_hours').value),
            importance: parseInt(formData.get('importance') || document.getElementById('importance').value),
            dependencies: []
        };

        // Validate task
        if (!this.validateTask(task)) {
            return;
        }

        this.tasks.push(task);
        this.updateTaskList();
        form.reset();
    }

    validateTask(task) {
        if (!task.title || !task.due_date || !task.estimated_hours || !task.importance) {
            this.showError('Please fill in all required fields');
            return false;
        }

        if (task.estimated_hours <= 0) {
            this.showError('Estimated hours must be greater than 0');
            return false;
        }

        if (task.importance < 1 || task.importance > 10) {
            this.showError('Importance must be between 1 and 10');
            return false;
        }

        return true;
    }

    updateTaskList() {
        const taskList = document.getElementById('added-tasks');
        taskList.innerHTML = '';

        this.tasks.forEach((task, index) => {
            const li = document.createElement('li');
            li.innerHTML = `
                <strong>${task.title}</strong><br>
                Due: ${task.due_date} | Hours: ${task.estimated_hours} | Importance: ${task.importance}/10
                <button onclick="taskAnalyzer.removeTask(${index})" style="float: right; padding: 5px 10px; font-size: 12px;">Remove</button>
            `;
            taskList.appendChild(li);
        });
    }

    removeTask(index) {
        this.tasks.splice(index, 1);
        this.updateTaskList();
    }

    async analyzeTasks() {
        let tasksToAnalyze = [];

        // Check which input method is active
        const activeTab = document.querySelector('.tab-content.active').id;
        
        if (activeTab === 'form-tab') {
            tasksToAnalyze = this.tasks;
        } else {
            // Bulk input
            const bulkInput = document.getElementById('bulk-input').value.trim();
            if (!bulkInput) {
                this.showError('Please enter tasks in JSON format or switch to single task input');
                return;
            }

            try {
                tasksToAnalyze = JSON.parse(bulkInput);
                if (!Array.isArray(tasksToAnalyze)) {
                    throw new Error('Input must be an array of tasks');
                }
            } catch (error) {
                this.showError('Invalid JSON format: ' + error.message);
                return;
            }
        }

        if (tasksToAnalyze.length === 0) {
            this.showError('Please add at least one task to analyze');
            return;
        }

        const strategy = document.getElementById('strategy').value;
        
        this.showLoading(true);
        this.hideError();

        try {
            const response = await fetch(`${this.apiBase}/analyze/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    tasks: tasksToAnalyze,
                    strategy: strategy
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to analyze tasks');
            }

            this.displayResults(data.tasks);
        } catch (error) {
            this.showError('Error analyzing tasks: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    async getSuggestions() {
        try {
            const response = await fetch(`${this.apiBase}/suggest/`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error('Failed to get suggestions');
            }

            this.displaySuggestions(data.suggested_tasks);
        } catch (error) {
            this.showError('Error getting suggestions: ' + error.message);
        }
    }

    displayResults(tasks) {
        const resultsDiv = document.getElementById('task-results');
        resultsDiv.innerHTML = '';

        tasks.forEach(task => {
            const taskDiv = document.createElement('div');
            taskDiv.className = `task-result ${this.getPriorityClass(task.priority_score)}`;
            
            const depCount = Array.isArray(task.dependencies) ? task.dependencies.length : 0;
            const depList = Array.isArray(task.dependencies) && task.dependencies.length > 0 ? 
                ` (${task.dependencies.join(', ')})` : '';
            
            taskDiv.innerHTML = `
                <div class="task-title">${task.title}</div>
                <div class="task-score">${task.priority_score}</div>
                <div class="task-details">
                    <div class="task-detail"><strong>Due:</strong> ${task.due_date}</div>
                    <div class="task-detail"><strong>Hours:</strong> ${task.estimated_hours}</div>
                    <div class="task-detail"><strong>Importance:</strong> ${task.importance}/10</div>
                    <div class="task-detail"><strong>Dependencies:</strong> ${depCount}${depList}</div>
                </div>
                <div class="task-explanation">${task.explanation}</div>
            `;
            
            resultsDiv.appendChild(taskDiv);
        });

        document.getElementById('results').classList.remove('hidden');
    }

    displaySuggestions(suggestions) {
        const suggestionsDiv = document.getElementById('suggestions-results');
        suggestionsDiv.innerHTML = '<h3>Top 3 Tasks for Today:</h3>';

        suggestions.forEach((task, index) => {
            const taskDiv = document.createElement('div');
            taskDiv.className = 'task-result high-priority';
            
            taskDiv.innerHTML = `
                <div class="task-title">#${index + 1}: ${task.title}</div>
                <div class="task-score">${task.priority_score}</div>
                <div class="task-details">
                    <div class="task-detail"><strong>Due:</strong> ${task.due_date}</div>
                    <div class="task-detail"><strong>Hours:</strong> ${task.estimated_hours}</div>
                    <div class="task-detail"><strong>Importance:</strong> ${task.importance}/10</div>
                </div>
                <div class="task-explanation">${task.explanation}</div>
            `;
            
            suggestionsDiv.appendChild(taskDiv);
        });
    }

    getPriorityClass(score) {
        if (score >= 0.7) return 'high-priority';
        if (score >= 0.5) return 'medium-priority';
        return 'low-priority';
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        if (show) {
            loading.classList.remove('hidden');
        } else {
            loading.classList.add('hidden');
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('error');
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }

    hideError() {
        document.getElementById('error').classList.add('hidden');
    }
}

// Initialize the application
const taskAnalyzer = new TaskAnalyzer();