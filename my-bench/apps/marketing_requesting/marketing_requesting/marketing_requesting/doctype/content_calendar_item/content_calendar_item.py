from __future__ import annotations

import frappe
from frappe.model.document import Document


class ContentCalendarItem(Document):
	def before_save(self):
		self._apply_defaults()
		self._set_calendar_color()

	def _apply_defaults(self):
		if not self.assigned_to:
			self.assigned_to = frappe.session.user

	def _set_calendar_color(self):
		priority_map = {
			"High": "#000000",
			"Medium": "#555555",
			"Low": "#999999",
		}
		self.color = priority_map.get(self.priority or "Medium", "#555555")
