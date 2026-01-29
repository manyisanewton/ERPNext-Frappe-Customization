from __future__ import annotations

import frappe


def execute(filters=None):
	top_departments = frappe.db.sql(
		"""
		select coalesce(department, 'Unspecified') as department, count(*) as requests
		from `tabMarketing Request`
		group by department
		order by requests desc
		limit 3
		""",
		as_dict=True,
	)
	top_request_types = frappe.db.sql(
		"""
		select coalesce(request_type, 'Unspecified') as request_type, count(*) as requests
		from `tabMarketing Request`
		group by request_type
		order by requests desc
		limit 3
		""",
		as_dict=True,
	)
	busy_periods = frappe.db.sql(
		"""
		select date_format(creation, '%Y-%m') as period, count(*) as requests
		from `tabMarketing Request`
		group by period
		order by requests desc
		limit 3
		""",
		as_dict=True,
	)

	open_requests = frappe.db.sql(
		"""
		select assigned_to, count(*) as requests
		from `tabMarketing Request`
		where assigned_to is not null
			and status in ('Assigned','Not Started','In Progress','Awaiting Information','Review')
		group by assigned_to
		""",
		as_dict=True,
	)

	avg_open = 0
	if open_requests:
		avg_open = sum(row["requests"] for row in open_requests) / len(open_requests)

	if avg_open > 5:
		capacity = "Overloaded"
		indicator = "Red"
	elif avg_open >= 2:
		capacity = "Balanced"
		indicator = "Blue"
	else:
		capacity = "Available"
		indicator = "Green"

	report_summary = [
		{
			"label": "Top Requesting Departments",
			"value": ", ".join(row["department"] for row in top_departments) or "None",
			"indicator": "Blue",
		},
		{
			"label": "Most Common Request Types",
			"value": ", ".join(row["request_type"] for row in top_request_types) or "None",
			"indicator": "Blue",
		},
		{
			"label": "Busiest Periods",
			"value": ", ".join(row["period"] for row in busy_periods) or "None",
			"indicator": "Blue",
		},
		{
			"label": "Team Capacity Status",
			"value": capacity,
			"indicator": indicator,
		},
	]

	return [], [], None, None, report_summary
