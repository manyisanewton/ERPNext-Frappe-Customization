from __future__ import annotations

import frappe
from frappe.model.document import Document


class MarketingRequest(Document):
	def before_save(self):
		self._set_requester_details()
		self._normalize_updates()
		self._set_assignment_status()

	def validate(self):
		self._validate_assignment_controls()
		self._validate_status_controls()

	def after_insert(self):
		self._notify_hod_new_request()

	def on_update(self):
		self._notify_assignment_changes()
		self._notify_status_changes()

	def _set_requester_details(self):
		if not self.requester:
			self.requester = frappe.session.user

		user_details = frappe.db.get_value(
			"User",
			self.requester,
			["full_name", "email", "phone"],
			as_dict=True,
		)
		if user_details:
			if not self.requester_name:
				self.requester_name = user_details.full_name
			if not self.contact_email:
				self.contact_email = user_details.email
			if not self.contact_phone:
				self.contact_phone = user_details.phone

	def _normalize_updates(self):
		last_status = None
		for update in self.get("updates", []):
			if not update.updated_by:
				update.updated_by = frappe.session.user
			if not update.update_date:
				update.update_date = frappe.utils.now_datetime()
			if update.status:
				last_status = update.status
		if last_status:
			self.status = last_status

	def _set_assignment_status(self):
		if self.assigned_to and self.status == "New":
			self.status = "Assigned"

	def _validate_assignment_controls(self):
		if self.has_value_changed("priority") or self.has_value_changed("assigned_to"):
			if not _has_role("Marketing HOD"):
				frappe.throw("Only Marketing HOD can assign priority or team members.")
		if (self.priority or self.assigned_to) and not _has_role("Marketing HOD"):
			frappe.throw("Only Marketing HOD can assign priority or team members.")

	def _validate_status_controls(self):
		if self.is_new() and self.status == "New":
			return

		if self.has_value_changed("status") or self.status != "New":
			if not (_has_role("Marketing HOD") or _has_role("Marketing Team")):
				frappe.throw("Only Marketing HOD or Marketing Team can update status.")

	def _notify_hod_new_request(self):
		users = _get_users_with_role("Marketing HOD")
		subject = f"New Marketing Request: {self.name}"
		_create_notification_logs(users, subject, self)

	def _notify_assignment_changes(self):
		if self.is_new() or not self.has_value_changed("assigned_to"):
			return

		if self.assigned_to:
			frappe.assign_to.add(
				{
					"assign_to": [self.assigned_to],
					"doctype": self.doctype,
					"name": self.name,
					"description": "Marketing request assigned to you.",
				}
			)
			_create_notification_logs(
				[self.assigned_to],
				f"Marketing Request Assigned: {self.name}",
				self,
			)

	def _notify_status_changes(self):
		if not self.has_value_changed("status"):
			return

		users = _get_users_with_role("Marketing HOD")
		if self.requester:
			users.append(self.requester)

		subject = f"Marketing Request {self.name} is now {self.status}"
		_create_notification_logs(users, subject, self)


def _get_users_with_role(role):
	return list(set(frappe.get_all("Has Role", filters={"role": role}, pluck="parent")))


def _has_role(role, user=None):
	return role in frappe.get_roles(user or frappe.session.user)


def _create_notification_logs(users, subject, doc):
	for user in set(users):
		if not user:
			continue
		frappe.get_doc(
			{
				"doctype": "Notification Log",
				"subject": subject,
				"for_user": user,
				"type": "Alert",
				"document_type": doc.doctype,
				"document_name": doc.name,
			}
		).insert(ignore_permissions=True)
