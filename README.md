# DevTrack

A minimal backend API for tracking engineering issues (bugs, priorities,
statuses) — a stripped-down GitHub Issues clone built with Django.

## How to run the project

1. **Clone the repo and enter it**
   ```bash
   git clone <your-repo-url>
   cd devtrack
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install django
   ```

3. **Apply migrations** (needed for Django's built-in apps like admin/auth;
   the actual issue/reporter data is stored separately in JSON files, not
   the database)
   ```bash
   python manage.py migrate
   ```

4. **Run the server**
   ```bash
   python manage.py runserver
   ```

   The API is now available at `http://127.0.0.1:8000/`.

5. **Test in Postman** using the endpoints below. `issues.json` and
   `reporters.json` are created automatically at the project root the
   first time you POST to an endpoint (they start out as `[]`).

## What each endpoint does

### Reporters

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/reporters/` | Create a new reporter. Body: `{"name": "...", "email": "...", "team": "..."}` (`id` optional — auto-assigned if omitted). Returns `201` + the created reporter, or `400` with a validation error. |
| GET | `/api/reporters/` | Get all reporters. |
| GET | `/api/reporters/?id=1` | Get a single reporter by ID. Returns `404` if it doesn't exist. |

### Issues

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/issues/` | Create a new issue. Body: `{"title", "description", "status", "priority", "reporter_id"}` (`id` optional). Instantiates `CriticalIssue`, `LowPriorityIssue`, or the base `Issue` class depending on `priority`, and returns `201` with the record plus a `message` field from `describe()`. Returns `400` with a validation error (e.g. empty title, invalid status/priority). |
| GET | `/api/issues/` | Get all issues. |
| GET | `/api/issues/?id=1` | Get a single issue by ID. Returns `404` if it doesn't exist. |
| GET | `/api/issues/?status=open` | Get all issues filtered by status (`open`, `in_progress`, `resolved`, `closed`). |

`created_at` is stamped automatically on issue creation using `str(datetime.now())`.

## Project structure

```
devtrack/
  manage.py
  issues.json          # data store for issues
  reporters.json        # data store for reporters
  devtrack/
    settings.py
    urls.py             # includes issues.urls under /api/
  issues/
    models.py           # OOP classes: BaseEntity, Reporter, Issue, CriticalIssue, LowPriorityIssue
    views.py            # JSON-file-backed endpoint logic
    urls.py
```

## Design decision

**Kept the OOP entity classes (`BaseEntity`, `Reporter`, `Issue`,
`CriticalIssue`, `LowPriorityIssue`) as plain Python classes in
`models.py`, completely separate from Django's ORM `Model` class and
from the view functions.** The views only ever talk to these classes
through `validate()`, `to_dict()`, and `describe()`, and a small
`build_issue()` factory picks the right subclass based on `priority`.
This means the request-handling code in `views.py` never branches on
priority-specific formatting logic itself — it just calls `describe()`
polymorphically — which keeps Parts A and B (validation/serialization
and inheritance/overriding) genuinely reusable and independently
testable, rather than mixed into the HTTP layer.

## Testing in Postman

Screenshots of at least one success (e.g. `POST /api/issues/` with a
critical-priority issue) and one failure (e.g. `POST /api/issues/`
with an empty `title`, or `GET /api/issues/?id=999`) should be added
here before submission.
