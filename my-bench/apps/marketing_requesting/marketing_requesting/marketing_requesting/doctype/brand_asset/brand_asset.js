frappe.ui.form.on("Brand Asset", {
	refresh(frm) {
		if (!frm.doc.status) {
			frm.set_value("status", "Draft");
		}
	},
});
