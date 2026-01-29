from __future__ import annotations

import frappe


def execute(filters=None):
	data = frappe.db.sql(
		"""
		select
			coalesce(department, 'Unspecified') as department,
			count(*) as requests
		from `tabMarketing Request`
		group by department
		order by requests desc
		""",
		as_dict=True,
	)

	columns = [
		{
			"label": "Department",
			"fieldname": "department",
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
			"labels": [row["department"] for row in data],
			"datasets": [{"name": "Requests", "values": [row["requests"] for row in data]}],
		},
		"type": "bar",
	}

	return columns, data, None, chart
