# Algo-AI: Algorithm Learning Platform

## Tech Stack

### Backend
- **Framework**: Django 5.1.4
- **Database**: SQLite3 (development)
- **Authentication**: Django's built-in authentication system
- **API**: Django REST Framework
- **WebSocket Support**: Django Channels (for real-time features)
- **Environment Management**: python-dotenv
- **CORS Handling**: django-cors-headers

### Frontend
- **Framework**: Vue.js 3 (Options API with Composition API in UI components)
- **Build Tool**: Vite
- **State Management**: Pinia
- **Routing**: Vue Router
- **Styling**: TailwindCSS
- **UI Components**: PrimeVue
- **Code Editing**: CodeMirror and Monaco Editor
- **Data Visualization**: Chart.js
- **Markdown Rendering**: Markdown-it

## Project Structure

### Backend Modules
- `accounts/`: User authentication and management
  - User registration and login
  - Profile management
  - Password reset functionality
  - Session handling
- `problems/`: Handling problem sets
  - Problem creation and management
  - Solution submission and validation
  - Test case management
  - Problem categorization and tagging
- `ai_chat/`: AI-assisted learning and chat functionality
  - Real-time chat with AI tutor
  - Context-aware responses
  - Learning progress tracking
  - Chat history management
- `code_execution/`: Code execution and testing
  - Secure code execution environment
  - Test case execution
  - Performance metrics collection
  - Code analysis and feedback
- `gamification/`: Gamification features and user progress tracking
  - Achievement system
  - Experience points and leveling
  - Badges and rewards
  - Progress tracking and statistics
- `plan/`: Learning path planning
  - Personalized learning paths
  - Progress tracking
  - Goal setting and achievement
  - Curriculum management

### Frontend Structure
- `src/views/uikit/`: Component library and documentation
  - Reusable UI components
  - Component documentation
  - Design system implementation
- `src/service/`: Service implementations
  - API integration services
  - State management services
  - Utility services
- `src/layout/`: Layout components
  - Main application layout
  - Navigation components
  - Responsive design components
- `src/codeLayout/`: Code-related view layouts
  - Code editor layouts
  - Problem view layouts
  - Solution submission layouts

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn
- Miniconda (recommended) or Anaconda
- OpenRouter API key (free)

### Environment Setup

#### Getting an OpenRouter API Key
1. Visit [OpenRouter](https://openrouter.ai/) and sign up for a free account
2. Navigate to your [API Keys](https://openrouter.ai/keys) page
3. Create a new API key
4. The free tier includes access to DeepSeek R1 model with generous usage limits
5. Add your API key to the `.env` file:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

#### Using Miniconda (Recommended)

1. **Install Miniconda**
   - Download [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
   - Follow the installation instructions for your operating system
   - Verify installation:
     ```bash
     conda --version
     ```

2. **Create and Activate Environment**
   ```bash
   # Create a new environment
   conda create -n algo-ai python=3.8
   
   # Activate the environment
   conda activate algo-ai
   ```

3. **Export Current Environment (if you have a working environment)**
   ```bash
   # Export the environment to a YAML file
   conda env export > environment.yml
   ```

4. **Import Environment (for new users)**
   ```bash
   # Create environment from YAML file
   conda env create -f environment.yml
   
   # Activate the environment
   conda activate algo-ai
   ```

#### Using Virtual Environment (Alternative)
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Backend Setup
1. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add required environment variables (refer to `.env.example`)

2. **Database Setup**
   - For development and testing, you can use the pre-populated mock database:
     ```bash
     # Copy the mock database to the project root
     cp mock_db/db.sqlite3 .
     ```
   The mock database includes sample algorithm problems with test cases

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Start the development server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup
1. **Install Node.js and npm**
   - Download and install Node.js from [https://nodejs.org/](https://nodejs.org/)
   - Verify installation:
     ```bash
     node --version
     npm --version
     ```

2. **Install Project Dependencies**
   ```bash
   # Navigate to frontend directory
   cd frontend
   
   # Install dependencies
   npm install
   ```

3. **Environment Configuration**
   - Create a `.env` file in the frontend directory
   - Add required environment variables:
     ```
     VITE_API_URL=http://localhost:8000
     VITE_WS_URL=ws://localhost:8000
     ```

4. **Start Development Server**
   ```bash
   # Start the Vite development server
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

5. **Build for Production**
   ```bash
   # Create production build
   npm run build
   ```

## Development with Mock Database

The project includes a `mock_db` directory containing a pre-populated SQLite database for testing and development. This database includes a collection of sample algorithm problems with their corresponding test cases.

### Using the Mock Database
1. **Initial Setup**
   ```bash
   # Copy the mock database to your project root
   cp mock_db/db.sqlite3 .
   ```

2. **Development Workflow**
   - Use the mock database to test problem-related features
   - Experiment with different problem types and test cases
   - The problems cover various difficulty levels and algorithmic concepts

3. **Resetting the Database**
   ```bash
   # To reset to the original mock database
   cp mock_db/db.sqlite3 .
   ```

Note: The mock database is for development purposes only. For production, you should set up a proper database and configure it according to your needs.

## Open Source Components

### Backend
- Django and its ecosystem
  - Django 5.1.4
  - Django REST Framework 3.15.2
  - Django CORS Headers 4.6.0
  - Django REST Framework SimpleJWT 5.3.1
- Core Python packages:
  - python-dotenv 1.0.1 (environment management)
  - requests 2.32.3 (HTTP API calls)
  - psycopg2 2.9.10 (PostgreSQL support)
  - pyjwt 2.10.1 (JWT handling)
- Standard Library modules used:
  - json (data serialization)
  - re (regular expressions for code sanitization)
  - html (HTML escaping for security)
  - threading (code execution timeout handling)
  - io (string buffer handling)
  - sys (system-specific parameters)
  - traceback (exception handling)
  - os (environment variables and file operations)
- Development tools:
  - flake8 7.1.1 (code linting)
  - pycodestyle 2.12.1 (PEP 8 style checking)
  - pyflakes 3.2.0 (static code analysis)
  - mccabe 0.7.0 (code complexity checking)

### Frontend
- PrimeVue components for UI elements
- CodeMirror and Monaco Editor for code editing
- Vue.js community plugins
- TailwindCSS utilities
- Chart.js for data visualization
- Markdown-it for markdown rendering

## AI-Assisted Development

This project has utilized Large Language Models (LLMs) for assistance in the following areas:
- Documentation (docstrings, module strings)
- Commit message generation
- Minor code improvements (error handling, logging, regular expressions)
- Code review suggestions

All core functionality, architecture, and implementation decisions were made and implemented by me. The AI assistance was used primarily for documentation and minor code improvements.

## Acknowledgments

- Fredrik Dahlqvist (Project Supervisor)
- Claire Revell (Module Organiser)
