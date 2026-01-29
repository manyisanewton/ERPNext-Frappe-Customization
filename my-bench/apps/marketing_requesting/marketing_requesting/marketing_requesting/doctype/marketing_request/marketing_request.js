frappe.ui.form.on("Marketing Request", {
	onload(frm) {
		if (frm.is_new()) {
			frm.set_value("requester", frappe.session.user);
			frm.set_value("requester_name", frappe.user.full_name());
		}
	},
	refresh(frm) {
		if (!frappe.user_roles.includes("Marketing HOD")) {
			return;
		}
		frm.add_custom_button(__("Suggest Assignee"), () => {
			frappe.call({
				method: "marketing_requesting.marketing_requesting.analytics.suggest_assignee",
				args: { request_name: frm.doc.name },
				callback: (r) => {
					if (r.message && r.message.user) {
						frm.set_value("assigned_to", r.message.user);
					} else {
						frappe.msgprint(__("No suitable assignee found."));
					}
				},
			});
		});
	},
});
