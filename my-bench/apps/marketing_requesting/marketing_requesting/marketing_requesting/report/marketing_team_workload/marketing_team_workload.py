from __future__ import annotations

import frappe

from marketing_requesting.marketing_requesting.analytics import (
	_get_open_statuses,
	_get_priority_weight,
)


def execute(filters=None):
	members = frappe.get_all(
		"Marketing Team Member",
		fields=["user", "skills", "status"],
		order_by="user asc",
	)

	open_data = frappe.db.sql(
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
	for row in open_data:
		workload.setdefault(row["assigned_to"], {})
		workload[row["assigned_to"]][row["priority"] or "Unassigned"] = row["requests"]

	rows = []
	for member in members:
		user = member.user
		priority_counts = workload.get(user, {})
		p1 = priority_counts.get("P1 - Revenue Critical", 0)
		p2 = priority_counts.get("P2 - Brand Growth", 0)
		p3 = priority_counts.get("P3 - Internal/Low", 0)
		total_weighted = (
			p1 * _get_priority_weight("P1 - Revenue Critical")
			+ p2 * _get_priority_weight("P2 - Brand Growth")
			+ p3 * _get_priority_weight("P3 - Internal/Low")
		)

		if total_weighted > 8:
			status = "Overloaded"
		elif total_weighted >= 4:
			status = "Busy"
		else:
			status = "Available"

		rows.append(
			{
				"user": user,
				"skills": member.skills,
				"p1": p1,
				"p2": p2,
				"p3": p3,
				"total_weighted": total_weighted,
				"status": status,
			}
		)

	columns = [
		{
			"label": "Team Member",
			"fieldname": "user",
			"fieldtype": "Link",
			"options": "User",
			"width": 200,
		},
		{"label": "Skills", "fieldname": "skills", "fieldtype": "Data", "width": 200},
		{"label": "P1", "fieldname": "p1", "fieldtype": "Int", "width": 80},
		{"label": "P2", "fieldname": "p2", "fieldtype": "Int", "width": 80},
		{"label": "P3", "fieldname": "p3", "fieldtype": "Int", "width": 80},
		{
			"label": "Total (Weighted)",
			"fieldname": "total_weighted",
			"fieldtype": "Int",
			"width": 140,
		},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
	]

	return columns, rows
