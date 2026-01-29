from __future__ import annotations

import frappe


def execute(filters=None):
	pending_statuses = [
		"New",
		"Assigned",
		"Not Started",
		"In Progress",
		"Awaiting Information",
		"Review",
	]

	data = frappe.db.sql(
		"""
		select
			coalesce(priority, 'Unassigned') as priority,
			count(*) as requests
		from `tabMarketing Request`
		where status in %(statuses)s
		group by priority
		order by requests desc
		""",
		{"statuses": tuple(pending_statuses)},
		as_dict=True,
	)

	columns = [
		{
			"label": "Priority",
			"fieldname": "priority",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": "Requests",
			"fieldname": "requests",
			"fieldtype": "Int",
			"width": 120,
		},
	]

	chart = {
		"data": {
			"labels": [row["priority"] for row in data],
			"datasets": [{"name": "Requests", "values": [row["requests"] for row in data]}],
		},
		"type": "bar",
	}

	return columns, data, None, chart
