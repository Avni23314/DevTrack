import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Reporter, Issue, CriticalIssue, LowPriorityIssue
from .storage import load_records, save_records, get_next_id, find_by_id

def read_request_data(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("Request body must contain valid JSON")
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object")
    return data

def error_response(message, status=400):
    return JsonResponse({"error": message}, status=status)

@csrf_exempt
def reporters_api(request):
    if request.method == "POST":
        try:
            data = read_request_data(request)
            name = data.get("name")
            email = data.get("email")
            team = data.get("team")
            reporter = Reporter(
                get_next_id("reporters"),
                name,
                email,
                team,
            )
            reporter.validate()
            records = load_records("reporters")
            records.append(reporter.to_dict())
            save_records("reporters", records)
            return JsonResponse(
                {
                    "message": "Reporter created successfully",
                    "reporter": reporter.to_dict(),
                },
                status=201,
            )
        except ValueError as exc:
            return error_response(str(exc))
    if request.method == "GET":
        record_id = request.GET.get("id")
        if record_id is not None:
            reporter = find_by_id("reporters", record_id)
            if reporter is None:
                return error_response("Reporter not found", 404)
            return JsonResponse(reporter)
        return JsonResponse({"reporters": load_records("reporters")})
    return error_response("Method not allowed", 405)

@csrf_exempt
def issues_api(request):
    if request.method == "POST":
        try:
            data = read_request_data(request)

            title = data.get("title")
            description = data.get("description", "")
            status = data.get("status", "open")
            priority = data.get("priority", "medium")
            reporter_id = data.get("reporter_id")
            if reporter_id is None:
                raise ValueError("reporter_id is required")
            if find_by_id("reporters", reporter_id) is None:
                raise ValueError("Reporter does not exist")
            issue_id = get_next_id("issues")
            if priority == "critical":
                issue = CriticalIssue(
                    issue_id, title, description, status,
                    priority, reporter_id
                )
            elif priority == "low":
                issue = LowPriorityIssue(
                    issue_id, title, description, status,
                    priority, reporter_id
                )
            else:
                issue = Issue(
                    issue_id, title, description, status,
                    priority, reporter_id
                )
            issue.validate()
            records = load_records("issues")
            records.append(issue.to_dict())
            save_records("issues", records)
            return JsonResponse(
                {
                    "message": issue.describe(),
                    "issue": issue.to_dict(),
                },
                status=201,
            )
        except ValueError as exc:
            return error_response(str(exc))
    if request.method == "GET":
        record_id = request.GET.get("id")
        requested_status = request.GET.get("status")
        records = load_records("issues")
        if record_id is not None:
            issue = find_by_id("issues", record_id)
            if issue is None:
                return error_response("Issue not found", 404)
            return JsonResponse(issue)
        if requested_status is not None:
            allowed_statuses = Issue.ALLOWED_STATUSES
            if requested_status not in allowed_statuses:
                return error_response("Invalid status filter")
            records = [
                issue for issue in records
                if issue.get("status") == requested_status
            ]
        return JsonResponse({"issues": records})
    return error_response("Method not allowed", 405)