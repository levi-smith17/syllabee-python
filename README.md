# Syllabee

> *The interactive syllabus management platform built for educators who believe course materials should be easy to maintain, easy to access, and actually engaging for students.*

Syllabee is a full-stack web application built in Python using the Django framework. It was created to solve a real problem: managing, updating, and distributing course syllabi across multiple sections and terms is tedious and error-prone when done manually. Syllabee makes it effortless.

The application is actively used by students at Edison State Community College each term and is available live at [syllabee.app](https://syllabee.app).

---

## What Syllabee Does

Syllabee serves syllabi both **interactively** (with dynamic, navigable content) and **statically** (as archived reference documents). It replaced an earlier system (IS3) by adding proper content management, interactive features, and a much cleaner student experience.

**For instructors:**
- Centralized syllabus management across multiple courses and terms
- Easy maintenance — update once, deploy everywhere
- Built-in editor for creating and revising course content
- Portfolio and curriculum management tools

**For students:**
- Access current and archived syllabi going back to Summer 2021
- Interactive, navigable course content rather than static PDFs
- Clean, consistent experience across all courses

---

## Project Structure

```
syllabee/
├── core/           # Core application logic and shared utilities
├── curriculum/     # Curriculum and course content management
├── editor/         # Syllabus editor interface
├── internship/     # Internship-related course materials
├── portfolio/      # Portfolio management module
├── syllabee/       # Main Django project configuration
├── templates/      # HTML templates
├── viewer/         # Syllabus viewer for students
├── manage.py       # Django management entry point
└── CHANGELOG.md    # Version history and release notes
```

---

## Tech Stack

- **Language:** Python
- **Framework:** [Django](https://www.djangoproject.com/)
- **Frontend:** HTML, JavaScript, SCSS
- **Deployment:** [syllabee.app](https://syllabee.app)
- **License:** GPL-3.0

---

## Background

Syllabee grew out of a frustration with the status quo. Managing syllabi across multiple courses — each with its own formatting, links, and term-specific details — was consuming time that should have been spent on teaching. The first iteration (IS3) solved the basic problem but quickly showed its limitations.

Syllabee was built from scratch in Python without AI assistance, as a deliberate exercise in full-stack Django development. It has been in active production use since December 2021 and continues to be maintained and improved each term.

---

## Live Application

Syllabee is live at **[syllabee.app](https://syllabee.app)**. Students from Edison State Community College can use it to access syllabi for current and past courses.

---

## Project Status

Syllabee is actively maintained. It is a personal/professional project and is not open for external contributions, but the codebase is available for review as a portfolio artifact demonstrating production Python and Django development.

---

## Getting Started (Local Development)

```bash
git clone https://github.com/levi-smith17/syllabee.git
cd syllabee
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open [http://localhost:8000](http://localhost:8000) to see the application.

---

*Built by [Levi Smith](https://levismith.us)*
