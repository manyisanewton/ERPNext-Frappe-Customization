frappe.ui.form.on("Content Calendar Item", {
	refresh(frm) {
		if (!frm.doc.assigned_to) {
			frm.set_value("assigned_to", frappe.session.user);
		}
	},
});
