from __future__ import annotations

import frappe


def execute(filters=None):
	data = frappe.db.sql(
		"""
		select
			date_format(creation, '%Y-%m') as period,
			count(*) as requests
		from `tabMarketing Request`
		group by period
		order by period
		""",
		as_dict=True,
	)

	columns = [
		{
			"label": "Period",
			"fieldname": "period",
			"fieldtype": "Data",
			"width": 120,
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
			"labels": [row["period"] for row in data],
			"datasets": [{"name": "Requests", "values": [row["requests"] for row in data]}],
		},
		"type": "line",
	}

	return columns, data, None, chart
