frappe.ui.form.on("Marketing Team Member", {
	refresh(frm) {
		if (!frm.doc.status) {
			frm.set_value("status", "Available");
		}
	},
});
