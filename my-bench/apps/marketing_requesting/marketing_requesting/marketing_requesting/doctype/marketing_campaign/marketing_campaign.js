frappe.ui.form.on("Marketing Campaign", {
	refresh(frm) {
		if (!frm.doc.campaign_owner) {
			frm.set_value("campaign_owner", frappe.session.user);
		}
	},
});
