from __future__ import annotations

import frappe
from frappe.model.document import Document


class MarketingTeamMember(Document):
	def validate(self):
		self._validate_unique_user()

	def _validate_unique_user(self):
		if not self.user:
			return
		exists = frappe.db.exists(
			"Marketing Team Member",
			{"user": self.user, "name": ["!=", self.name]},
		)
		if exists:
			frappe.throw("This user already has a Marketing Team Member profile.")
