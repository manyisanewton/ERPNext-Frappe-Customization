import frappe


def execute():
	for role in ["Marketing HOD", "Marketing Team"]:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role}).insert()
