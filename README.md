# Blog Platform

A platform for creating, editing, and viewing articles with photo attachments. Supports AI-powered content generation via OpenAI API.

---

## Technologies Used

- Python 3.13  
- Django 5.x  
- Django Class-Based Views (ListView, DetailView, CreateView, UpdateView, DeleteView)  
- Django Forms + Formsets (for photos)  
- OpenAI API for content generation  
- SQLite (default, can be replaced)   

---

## Getting Started

1. Clone the repository:

```bash
git clone <repository-url>
cd blog-platform
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.\.venv\Scripts\activate    # Windows
```

3. Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.\.venv\Scripts\activate    # Windows
```

4. Configure environment variables (e.g., in .env):
5. 
```bash
DJANGO_SETTINGS_MODULE=blog_project.settings

OPENAI_API_KEY=<your OpenAI API key>
```

6. Install dependencies:

```bash
python manage.py makemigration
python manage.py migrate
```

7. Run the development server:

```bash
http://127.0.0.1:8000/articles/
```