from __future__ import annotations

import frappe


def execute(filters=None):
	start_date = frappe.utils.get_first_day(frappe.utils.nowdate())

	data = frappe.db.sql(
		"""
		select
			coalesce(department, 'Unspecified') as department,
			count(*) as requests
		from `tabMarketing Request`
		where creation >= %s
		group by department
		order by requests desc
		""",
		start_date,
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

	return columns, data
