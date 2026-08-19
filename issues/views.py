import json
import os
from datetime import datetime

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from issues.models import Reporter, build_issue, VALID_STATUSES, VALID_PRIORITIES

REPORTERS_FILE = os.path.join(settings.BASE_DIR, 'reporters.json')
ISSUES_FILE = os.path.join(settings.BASE_DIR, 'issues.json')


# ---------------------------------------------------------------------
# JSON file storage helpers
# ---------------------------------------------------------------------

def _read_json_file(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        content = f.read().strip()
        if not content:
            return []
        return json.loads(content)


def _write_json_file(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def _next_id(records):
    if not records:
        return 1
    return max(record['id'] for record in records) + 1


def _parse_body(request):
    if not request.body:
        return {}
    return json.loads(request.body.decode('utf-8'))


# ---------------------------------------------------------------------
# Reporter endpoints
# ---------------------------------------------------------------------

@csrf_exempt
@require_http_methods(['GET', 'POST'])
def reporters_view(request):
    if request.method == 'POST':
        return _create_reporter(request)
    return _get_reporters(request)


def _create_reporter(request):
    try:
        data = _parse_body(request)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    reporters = _read_json_file(REPORTERS_FILE)
    reporter_id = data.get('id') or _next_id(reporters)

    reporter = Reporter(
        id=reporter_id,
        name=data.get('name'),
        email=data.get('email'),
        team=data.get('team'),
    )

    try:
        reporter.validate()
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    reporters.append(reporter.to_dict())
    _write_json_file(REPORTERS_FILE, reporters)

    return JsonResponse(reporter.to_dict(), status=201)


def _get_reporters(request):
    reporters = _read_json_file(REPORTERS_FILE)

    reporter_id = request.GET.get('id')
    if reporter_id is not None:
        try:
            reporter_id = int(reporter_id)
        except ValueError:
            return JsonResponse({'error': 'id must be an integer'}, status=400)

        for reporter in reporters:
            if reporter['id'] == reporter_id:
                return JsonResponse(reporter, status=200)
        return JsonResponse({'error': 'Reporter not found'}, status=404)

    return JsonResponse(reporters, safe=False, status=200)


# ---------------------------------------------------------------------
# Issue endpoints
# ---------------------------------------------------------------------

@csrf_exempt
@require_http_methods(['GET', 'POST'])
def issues_view(request):
    if request.method == 'POST':
        return _create_issue(request)
    return _get_issues(request)


def _create_issue(request):
    try:
        data = _parse_body(request)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    issues = _read_json_file(ISSUES_FILE)
    issue_id = data.get('id') or _next_id(issues)

    issue = build_issue(
        id=issue_id,
        title=data.get('title'),
        description=data.get('description'),
        status=data.get('status'),
        priority=data.get('priority'),
        reporter_id=data.get('reporter_id'),
        created_at=str(datetime.now()),
    )

    try:
        issue.validate()
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    issues.append(issue.to_dict())
    _write_json_file(ISSUES_FILE, issues)

    response_data = issue.to_dict()
    response_data['message'] = issue.describe()
    return JsonResponse(response_data, status=201)


def _get_issues(request):
    issues = _read_json_file(ISSUES_FILE)

    issue_id = request.GET.get('id')
    status = request.GET.get('status')

    if issue_id is not None:
        try:
            issue_id = int(issue_id)
        except ValueError:
            return JsonResponse({'error': 'id must be an integer'}, status=400)

        for issue in issues:
            if issue['id'] == issue_id:
                return JsonResponse(issue, status=200)
        return JsonResponse({'error': 'Issue not found'}, status=404)

    if status is not None:
        if status not in VALID_STATUSES:
            return JsonResponse(
                {'error': f'status must be one of {VALID_STATUSES}'}, status=400
            )
        filtered = [issue for issue in issues if issue['status'] == status]
        return JsonResponse(filtered, safe=False, status=200)

    return JsonResponse(issues, safe=False, status=200)
