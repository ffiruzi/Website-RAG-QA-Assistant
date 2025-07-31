# Website RAG Q&A System Backend

This is the backend API for the Website RAG Q&A System, a powerful tool that enables website owners to add intelligent question-answering capabilities to their sites using Retrieval-Augmented Generation (RAG).

## Features

- **Website Management**: Add, update, and delete websites to be crawled
- **Content Crawling**: Automated extraction of content from websites
- **Vector Embeddings**: Store and search content using vector embeddings
- **RAG-Powered Answers**: Generate accurate answers based on website content
- **Conversation History**: Track and manage user conversations

## Tech Stack

- **FastAPI**: Modern, high-performance web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **LangChain**: Framework for LLM applications
- **FAISS**: Efficient similarity search
- **OpenAI API**: For embeddings and completions

## Project Structure

```
backend/
├── alembic/              # Database migrations
├── app/                  # Application code
│   ├── api/              # API endpoints
│   │   ├── endpoints/    # Route handlers
│   │   └── dependencies/ # API dependencies
│   ├── core/             # Core modules
│   ├── db/               # Database initialization
│   ├── models/           # SQLAlchemy models
│   ├── repositories/     # Data access layer
│   ├── schemas/          # Pydantic models
│   └── services/         # Business logic
├── scripts/              # Utility scripts
└── tests/                # Unit and integration tests
```

## Getting Started

### Prerequisites

- Python 3.10 or higher
- PostgreSQL (or SQLite for development)
- OpenAI API key

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/Website-RAG-QA.git
   cd Website-RAG-QA/backend
   ```

2. Set up a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```
   DATABASE_URL=sqlite:///./app.db
   OPENAI_API_KEY=your_openai_api_key
   ```

### Database Setup

1. Run migrations to create the database schema
   ```bash
   python scripts/run_migrations.py
   ```

2. Or create a new migration if you've made model changes
   ```bash
   python scripts/create_migration.py "description of changes"
   ```

### Running the API

Start the development server:
```bash
python run_api.py
```

The API will be available at http://localhost:8000.

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /health` - Check if the API is running

### Websites
- `GET /api/websites/` - List all websites
- `POST /api/websites/` - Create a new website
- `GET /api/websites/{website_id}` - Get a specific website
- `PUT /api/websites/{website_id}` - Update a website
- `DELETE /api/websites/{website_id}` - Delete a website

## Development

### Running Tests

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app tests/
```

### Code Quality

Format code with Black:
```bash
black app tests
```

Sort imports with isort:
```bash
isort app tests
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./app.db` |
| `OPENAI_API_KEY` | OpenAI API key | None |
| `DEBUG` | Enable debug mode | `True` |
| `ENVIRONMENT` | Environment (development/production) | `development` |

## Implementation Progress

- ✅ Day 1: Project Setup and Repository Initialization
- ✅ Day 2: Database Setup and API Foundations
- ✅ Day 3: Web Crawling Implementation
- ✅ Day 4: Document Processing and Vector Storage
- ⬜ Day 5: RAG Implementation with LangChain
- ⬜ Day 6: API Integration and Backend Completion
- ⬜ Day 7: Frontend Foundation - Admin Dashboard Part 1
- ⬜ Day 8: Admin Dashboard Part 2 - Monitoring and Analytics
- ⬜ Day 9: Chat Widget UI Implementation
- ⬜ Day 10: Widget Integration with Backend
- ⬜ Day 11: Widget Embedding and Integration
- ⬜ Day 12: Performance Optimization and Security
- ⬜ Day 13: Testing and Documentation
- ⬜ Day 14: Deployment and Launch Preparation

## License

This project is licensed under the MIT License - see the LICENSE file for details.