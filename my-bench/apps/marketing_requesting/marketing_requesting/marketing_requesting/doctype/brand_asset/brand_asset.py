from __future__ import annotations

import frappe
from frappe.model.document import Document


def _user_has_role(user, role):
	return role in frappe.get_roles(user)


class BrandAsset(Document):
	def before_save(self):
		self._normalize_versions()
		self._apply_approval_metadata()

	def validate(self):
		self._validate_approval_controls()

	def _normalize_versions(self):
		latest_seen = None
		for version in self.get("versions", []):
			if not version.uploaded_by:
				version.uploaded_by = frappe.session.user
			if not version.uploaded_on:
				version.uploaded_on = frappe.utils.now_datetime()
			if version.is_latest:
				latest_seen = version

		if latest_seen:
			for version in self.get("versions", []):
				version.is_latest = 1 if version == latest_seen else 0

	def _apply_approval_metadata(self):
		if self.status == "Approved" and not self.approved_by:
			self.approved_by = frappe.session.user
			self.approved_on = frappe.utils.now_datetime()

	def _validate_approval_controls(self):
		if self.is_new():
			return

		if self.has_value_changed("is_public") or self.has_value_changed("status"):
			if not _user_has_role(frappe.session.user, "Marketing HOD"):
				frappe.throw("Only Marketing HOD can approve or publish assets.")


def brand_asset_query_conditions(user):
	if _user_has_role(user, "Marketing HOD") or _user_has_role(user, "Marketing Team"):
		return ""
	return "(is_public = 1)"


def brand_asset_has_permission(doc, user):
	if _user_has_role(user, "Marketing HOD") or _user_has_role(user, "Marketing Team"):
		return True
	if doc.is_public:
		return True
	return doc.owner == user
