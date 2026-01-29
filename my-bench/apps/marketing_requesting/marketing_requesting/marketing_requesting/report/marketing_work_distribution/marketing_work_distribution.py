from __future__ import annotations

import frappe


def execute(filters=None):
	data = frappe.db.sql(
		"""
		select
			assigned_to as team_member,
			count(*) as requests
		from `tabMarketing Request`
		where assigned_to is not null
			and status in ('Assigned','Not Started','In Progress','Awaiting Information','Review')
		group by assigned_to
		order by requests desc
		""",
		as_dict=True,
	)

	columns = [
		{
			"label": "Team Member",
			"fieldname": "team_member",
			"fieldtype": "Link",
			"options": "User",
			"width": 200,
		},
		{
			"label": "Open Requests",
			"fieldname": "requests",
			"fieldtype": "Int",
			"width": 140,
		},
	]

	chart = {
		"data": {
			"labels": [row["team_member"] for row in data],
			"datasets": [{"name": "Open Requests", "values": [row["requests"] for row in data]}],
		},
		"type": "pie",
	}

	return columns, data, None, chart
