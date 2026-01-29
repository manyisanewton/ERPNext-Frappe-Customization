from __future__ import annotations

import frappe


def execute(filters=None):
	data = frappe.db.sql(
		"""
		select
			name,
			campaign_name,
			campaign_type,
			start_date,
			end_date,
			budget_allocated,
			actual_spend,
			revenue_target,
			revenue_achieved,
			roi,
			status,
			campaign_owner
		from `tabMarketing Campaign`
		order by modified desc
		""",
		as_dict=True,
	)

	columns = [
		{
			"label": "Campaign",
			"fieldname": "campaign_name",
			"fieldtype": "Data",
			"width": 220,
		},
		{
			"label": "Type",
			"fieldname": "campaign_type",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": "Start Date",
			"fieldname": "start_date",
			"fieldtype": "Date",
			"width": 110,
		},
		{
			"label": "End Date",
			"fieldname": "end_date",
			"fieldtype": "Date",
			"width": 110,
		},
		{
			"label": "Budget",
			"fieldname": "budget_allocated",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": "Actual Spend",
			"fieldname": "actual_spend",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": "Revenue Target",
			"fieldname": "revenue_target",
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"label": "Revenue Achieved",
			"fieldname": "revenue_achieved",
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"label": "ROI",
			"fieldname": "roi",
			"fieldtype": "Float",
			"width": 80,
		},
		{
			"label": "Status",
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"label": "Owner",
			"fieldname": "campaign_owner",
			"fieldtype": "Link",
			"options": "User",
			"width": 160,
		},
	]

	return columns, data
