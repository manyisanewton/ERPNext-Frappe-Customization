import frappe


def get_context(context):
	context.no_cache = 1
	context.tasks = frappe.db.sql(
		"""
		select
			name,
			request_type,
			deadline_date,
			status
		from `tabMarketing Request`
		where priority like 'P1%%'
			and status in ('Assigned', 'Not Started', 'In Progress', 'Awaiting Information', 'Review')
		order by deadline_date asc, modified desc
		""",
		as_dict=True,
	)
