from __future__ import annotations

import frappe


@frappe.whitelist()
def get_completed_this_month():
	start_date = frappe.utils.get_first_day(frappe.utils.nowdate())
	count = frappe.db.count(
		"Marketing Request",
		filters={"status": "Completed", "modified": (">=", start_date)},
	)
	return {
		"value": count,
		"fieldtype": "Int",
		"route": ["List", "Marketing Request", "List"],
		"route_options": {"status": "Completed"},
	}


@frappe.whitelist()
def get_budget_utilization():
	result = frappe.db.sql(
		"""
		select
			sum(actual_spend) as actual_spend,
			sum(budget_allocated) as budget_allocated
		from `tabMarketing Campaign`
		where budget_allocated is not null
			and budget_allocated > 0
		""",
		as_dict=True,
	)
	actual_spend = (result[0] or {}).get("actual_spend") or 0
	budget_allocated = (result[0] or {}).get("budget_allocated") or 0
	value = (actual_spend / budget_allocated * 100) if budget_allocated else 0
	return {
		"value": round(value, 2),
		"fieldtype": "Percent",
		"route": ["List", "Marketing Campaign", "List"],
	}


@frappe.whitelist()
def get_average_turnaround_time():
	result = frappe.db.sql(
		"""
		select avg(timestampdiff(day, creation, modified)) as avg_days
		from `tabMarketing Request`
		where status = 'Completed'
		""",
		as_dict=True,
	)
	value = (result[0] or {}).get("avg_days") or 0
	return {
		"value": round(value, 2),
		"fieldtype": "Float",
		"route": ["query-report", "Marketing Turnaround Time"],
	}


def _get_open_statuses():
	return [
		"New",
		"Assigned",
		"Not Started",
		"In Progress",
		"Awaiting Information",
		"Review",
	]


def _get_priority_weight(priority):
	weights = {
		"P1 - Revenue Critical": 3,
		"P2 - Brand Growth": 2,
		"P3 - Internal/Low": 1,
	}
	return weights.get(priority, 1)


@frappe.whitelist()
def get_team_workload():
	data = frappe.db.sql(
		"""
		select assigned_to, priority, count(*) as requests
		from `tabMarketing Request`
		where assigned_to is not null
			and status in %(statuses)s
		group by assigned_to, priority
		""",
		{"statuses": tuple(_get_open_statuses())},
		as_dict=True,
	)

	workload = {}
	for row in data:
		user = row["assigned_to"]
		if not user:
			continue
		workload.setdefault(user, {})
		workload[user][row["priority"] or "Unassigned"] = row["requests"]
	return workload


def _is_user_blocked(user):
	today = frappe.utils.nowdate()
	rows = frappe.db.sql(
		"""
		select parent
		from `tabMarketing Team Availability`
		where parent in (
			select name from `tabMarketing Team Member` where user = %s
		)
			and ifnull(block_capacity, 0) = 1
			and %s between ifnull(from_date, '0001-01-01') and ifnull(to_date, '9999-12-31')
		limit 1
		""",
		(user, today),
		as_dict=True,
	)
	return bool(rows)


@frappe.whitelist()
def suggest_assignee(request_name=None):
	if not request_name:
		return {}
	request = frappe.get_doc("Marketing Request", request_name)
	open_workload = get_team_workload()

	skill_map = {
		"needed_poster_flyer": "Design",
		"needed_social_media": "Social Media",
		"needed_video_reel": "Video",
		"needed_brochure_profile": "Design",
		"needed_presentation_proposal": "Content",
	}
	required_skills = set()
	for fieldname, skill in skill_map.items():
		if getattr(request, fieldname, 0):
			required_skills.add(skill)

	members = frappe.get_all(
		"Marketing Team Member",
		fields=_get_team_member_fields(),
	)

	best = None
	best_score = None
	for member in members:
		if not member.user or _is_user_blocked(member.user):
			continue
		member_skills = set((member.get("skills") or "").split("\n")) if member.get("skills") else set()
		if required_skills and not required_skills.intersection(member_skills):
			continue

		priority_counts = open_workload.get(member.user, {})
		score = 0
		for priority, count in priority_counts.items():
			score += _get_priority_weight(priority) * count
		if best_score is None or score < best_score:
			best_score = score
			best = member.user

	return {
		"user": best,
		"required_skills": sorted(required_skills),
		"score": best_score,
	}


def _get_team_member_fields():
	fields = ["name", "user"]
	if frappe.db.has_column("Marketing Team Member", "skills"):
		fields.append("skills")
	return fields
