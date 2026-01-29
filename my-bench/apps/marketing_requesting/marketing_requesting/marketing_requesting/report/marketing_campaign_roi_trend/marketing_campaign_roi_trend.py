from __future__ import annotations

import frappe


def execute(filters=None):
	data = frappe.db.sql(
		"""
		select
			date_format(coalesce(end_date, start_date), '%Y-%m') as period,
			avg(roi) as avg_roi
		from `tabMarketing Campaign`
		where coalesce(end_date, start_date) is not null
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
			"label": "Average ROI",
			"fieldname": "avg_roi",
			"fieldtype": "Float",
			"width": 140,
		},
	]

	chart = {
		"data": {
			"labels": [row["period"] for row in data],
			"datasets": [{"name": "Average ROI", "values": [row["avg_roi"] for row in data]}],
		},
		"type": "line",
	}

	return columns, data, None, chart
