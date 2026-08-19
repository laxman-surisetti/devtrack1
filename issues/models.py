"""
Plain Python OOP data model for DevTrack.

These are NOT Django ORM models. Per the assignment brief, data is
modeled with plain Python classes (BaseEntity -> Reporter / Issue)
and persisted manually to JSON files (issues.json / reporters.json).
Keeping this logic out of views.py keeps the OOP design testable and
independent of the web framework.
"""

from abc import ABC, abstractmethod

VALID_STATUSES = ('open', 'in_progress', 'resolved', 'closed')
VALID_PRIORITIES = ('low', 'medium', 'high', 'critical')


class BaseEntity(ABC):
    """Abstract base class shared by all DevTrack entities."""

    @abstractmethod
    def validate(self):
        """Raise ValueError if the entity's data is invalid."""
        pass

    def to_dict(self):
        """Serialize the entity's attributes to a plain dict."""
        return {
            key: value
            for key, value in self.__dict__.items()
        }


class Reporter(BaseEntity):
    """A person who files issues."""

    def __init__(self, id, name, email, team):
        self.id = id
        self.name = name
        self.email = email
        self.team = team

    def validate(self):
        if not self.name:
            raise ValueError('Name cannot be empty')
        if not self.email or '@' not in self.email:
            raise ValueError('Invalid email')
        if not self.team:
            raise ValueError('Team cannot be empty')


class Issue(BaseEntity):
    """A bug report or task filed by a Reporter."""

    def __init__(self, id, title, description, status, priority, reporter_id, created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.reporter_id = reporter_id
        self.created_at = created_at

    def validate(self):
        if not self.title:
            raise ValueError('Title cannot be empty')
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Status must be one of {VALID_STATUSES}")
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of {VALID_PRIORITIES}")
        if self.reporter_id is None:
            raise ValueError('reporter_id is required')

    def describe(self):
        return f"{self.title} [{self.priority}]"


class CriticalIssue(Issue):
    """Issue subclass for priority == 'critical'. Overrides describe()."""

    def describe(self):
        return f"[URGENT] {self.title} — needs immediate attention"


class LowPriorityIssue(Issue):
    """Issue subclass for priority == 'low'. Overrides describe()."""

    def describe(self):
        return f"{self.title} — low priority, handle when free"


def build_issue(id, title, description, status, priority, reporter_id, created_at=None):
    """
    Factory that instantiates the correct Issue subclass based on priority.
    Used by the POST /api/issues/ view so the branching logic lives in one
    place instead of being duplicated in views.py.
    """
    kwargs = dict(
        id=id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        reporter_id=reporter_id,
        created_at=created_at,
    )
    if priority == 'critical':
        return CriticalIssue(**kwargs)
    elif priority == 'low':
        return LowPriorityIssue(**kwargs)
    else:
        return Issue(**kwargs)
