from __future__ import annotations

import frappe


def execute(filters=None):
	data = frappe.db.sql(
		"""
		select
			coalesce(priority, 'Unassigned') as priority,
			avg(timestampdiff(day, creation, modified)) as avg_days
		from `tabMarketing Request`
		where status = 'Completed'
		group by priority
		order by avg_days desc
		""",
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
			"label": "Average Days to Complete",
			"fieldname": "avg_days",
			"fieldtype": "Float",
			"width": 180,
		},
	]

	return columns, data
