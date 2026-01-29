from __future__ import annotations

import frappe


def execute(filters=None):
	data = frappe.db.sql(
		"""
		select
			assigned_to as team_member,
			count(*) as completed
		from `tabMarketing Request`
		where status = 'Completed'
			and assigned_to is not null
		group by assigned_to
		order by completed desc
		""",
		as_dict=True,
	)

	columns = [
		{
			"label": "Team Member",
			"fieldname": "team_member",
			"fieldtype": "Link",
			"options": "User",
			"width": 220,
		},
		{
			"label": "Tasks Completed",
			"fieldname": "completed",
			"fieldtype": "Int",
			"width": 140,
		},
	]

	return columns, data
