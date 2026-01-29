frappe.views.calendar["Content Calendar Item"] = {
	field_map: {
		start: "start_datetime",
		end: "end_datetime",
		id: "name",
		allDay: "all_day",
		title: "item_title",
		status: "item_type",
		color: "color",
	},
	style_map: {
		"Social Post": "info",
		"Email Campaign": "success",
		Event: "warning",
		"Content Publish": "primary",
		Deadline: "danger",
	},
	get_events_method: "frappe.desk.calendar.get_events",
};
