from __future__ import annotations

import itertools

import frappe
from frappe.utils import add_days, nowdate
from marketing_requesting.marketing_requesting.doctype.marketing_request.marketing_request import (
	MarketingRequest,
)


def _get_enabled_users():
	users = frappe.get_all("User", filters={"enabled": 1}, fields=["name"])
	return [user["name"] for user in users if user["name"] != "Guest"]


def _pick_department(preferred, available):
	if preferred and frappe.db.exists("Department", preferred):
		return preferred
	if available:
		return available[0]
	return None


def create_demo_data():
	"""Create demo data for Marketing Requesting."""
	users = _get_enabled_users()
	if not users:
		return {"created": 0, "skipped": 0, "detail": "No enabled users found."}

	primary_user = users[0]
	secondary_user = users[1] if len(users) > 1 else users[0]
	today = nowdate()

	available_departments = [
		name
		for name in ["Marketing", "Sales", "Operations", "Human Resources", "Accounts"]
		if frappe.db.exists("Department", name)
	]
	dept_cycle = itertools.cycle(available_departments) if available_departments else None

	created = 0
	skipped = 0

	campaign_specs = [
		{
			"campaign_name": "Demo: Q1 Brand Lift",
			"campaign_type": "Brand Awareness",
			"campaign_owner": primary_user,
			"status": "Active",
			"start_date": add_days(today, -30),
			"end_date": add_days(today, 30),
			"budget_allocated": 10000,
			"actual_spend": 4200,
			"roi": 1.6,
			"channels": "Social Media\nEmail",
			"target_audience": "Prospects and partners",
		},
		{
			"campaign_name": "Demo: Launch Sprint",
			"campaign_type": "Product Launch",
			"campaign_owner": secondary_user,
			"status": "Completed",
			"start_date": add_days(today, -90),
			"end_date": add_days(today, -60),
			"budget_allocated": 8000,
			"actual_spend": 9200,
			"roi": 1.2,
			"channels": "Digital Ads\nEvents",
			"target_audience": "Existing customers",
		},
	]

	campaign_names = []
	for spec in campaign_specs:
		if frappe.db.exists("Marketing Campaign", {"campaign_name": spec["campaign_name"]}):
			skipped += 1
			continue
		doc = frappe.get_doc({"doctype": "Marketing Campaign", **spec})
		doc.insert(ignore_permissions=True)
		campaign_names.append(doc.name)
		created += 1

	if not campaign_names:
		existing = frappe.get_all(
			"Marketing Campaign",
			fields=["name"],
			limit=1,
		)
		if existing:
			campaign_names.append(existing[0]["name"])

	team_members = [
		{
			"user": primary_user,
			"skills": "Design\nContent",
			"capacity_per_week": 6,
			"status": "Available",
		},
		{
			"user": secondary_user,
			"skills": "Video\nSocial Media",
			"capacity_per_week": 5,
			"status": "Busy",
		},
	]
	for member in team_members:
		if frappe.db.exists("Marketing Team Member", {"user": member["user"]}):
			skipped += 1
			continue
		doc = frappe.get_doc({"doctype": "Marketing Team Member", **member})
		doc.insert(ignore_permissions=True)
		created += 1

	asset_specs = [
		{
			"asset_name": "Demo: Brand Guidelines v1",
			"category": "Logos & Brand Guidelines",
			"asset_type": "Guideline",
			"campaign": campaign_names[0] if campaign_names else None,
			"status": "Approved",
			"is_public": 1,
		},
		{
			"asset_name": "Demo: Product Hero Images",
			"category": "Product Images & Videos",
			"asset_type": "Image",
			"campaign": campaign_names[0] if campaign_names else None,
			"status": "Submitted",
			"is_public": 0,
		},
	]
	for asset in asset_specs:
		if frappe.db.exists("Brand Asset", {"asset_name": asset["asset_name"]}):
			skipped += 1
			continue
		doc = frappe.get_doc({"doctype": "Brand Asset", **asset})
		doc.insert(ignore_permissions=True)
		created += 1

	request_specs = [
		{
			"objective": "Demo - Landing page refresh",
			"request_type": "Marketing/Awareness",
			"department": _pick_department("Marketing", available_departments),
			"status": "New",
			"priority": "P2 - Brand Growth",
			"assigned_to": primary_user,
			"needed_social_media": 1,
			"deadline_date": add_days(today, 10),
		},
		{
			"objective": "Demo - Sales enablement deck",
			"request_type": "Sales/Revenue Support",
			"department": _pick_department("Sales", available_departments),
			"status": "Assigned",
			"priority": "P1 - Revenue Critical",
			"assigned_to": secondary_user,
			"needed_presentation_proposal": 1,
			"deadline_date": add_days(today, 5),
		},
		{
			"objective": "Demo - Event booth assets",
			"request_type": "Event/Activation",
			"department": _pick_department("Operations", available_departments),
			"status": "In Progress",
			"priority": "P2 - Brand Growth",
			"assigned_to": primary_user,
			"needed_poster_flyer": 1,
			"deadline_date": add_days(today, 21),
		},
		{
			"objective": "Demo - Internal newsletter",
			"request_type": "Internal Communication",
			"department": _pick_department("Human Resources", available_departments),
			"status": "Review",
			"priority": "P3 - Internal/Low",
			"assigned_to": secondary_user,
			"needed_other": "Email newsletter template",
			"deadline_date": add_days(today, 7),
		},
		{
			"objective": "Demo - Compliance update flyer",
			"request_type": "Compliance/Corporate",
			"department": _pick_department("Accounts", available_departments),
			"status": "Completed",
			"priority": "P3 - Internal/Low",
			"assigned_to": primary_user,
			"needed_poster_flyer": 1,
			"deadline_date": add_days(today, -2),
		},
		{
			"objective": "Demo - Product launch video",
			"request_type": "Marketing/Awareness",
			"department": _pick_department(None, available_departments),
			"status": "Completed",
			"priority": "P1 - Revenue Critical",
			"assigned_to": secondary_user,
			"needed_video_reel": 1,
			"deadline_date": add_days(today, -5),
		},
	]

	original_notify = MarketingRequest._notify_hod_new_request
	original_assignment_notify = MarketingRequest._notify_assignment_changes
	original_status_notify = MarketingRequest._notify_status_changes
	MarketingRequest._notify_hod_new_request = lambda self: None
	MarketingRequest._notify_assignment_changes = lambda self: None
	MarketingRequest._notify_status_changes = lambda self: None

	try:
		for idx, spec in enumerate(request_specs, start=1):
			update_status = spec["status"]
			if update_status not in {
				"Not Started",
				"In Progress",
				"Awaiting Information",
				"Review",
				"Completed",
			}:
				update_status = "Not Started"

			if frappe.db.exists("Marketing Request", {"objective": spec["objective"]}):
				skipped += 1
				continue

			department = spec.get("department") or (next(dept_cycle) if dept_cycle else None)
			doc = frappe.get_doc(
				{
					"doctype": "Marketing Request",
					"requester": primary_user,
					"requester_name": "Demo Requester",
					"department": department,
					"contact_email": primary_user,
					"contact_phone": "555-010{}".format(idx),
					"audience": "Clients",
					"revenue_linked": 1 if spec["priority"].startswith("P1") else 0,
					"updates": [
						{
							"status": update_status,
							"update_notes": "Demo update for {}".format(spec["objective"]),
						}
					],
					"deliverables": [
						{
							"description": "Draft deliverable for {}".format(
								spec["objective"]
							),
						}
					],
					**spec,
				}
			)
			doc.flags.ignore_validate = True
			doc.insert(ignore_permissions=True)
			created += 1

			if spec["status"] == "Completed":
				created_on = add_days(today, -30 - idx)
				modified_on = add_days(today, -2)
				frappe.db.sql(
					"""
					update `tabMarketing Request`
					set creation = %s, modified = %s
					where name = %s
					""",
					(created_on, modified_on, doc.name),
				)
	finally:
		MarketingRequest._notify_hod_new_request = original_notify
		MarketingRequest._notify_assignment_changes = original_assignment_notify
		MarketingRequest._notify_status_changes = original_status_notify

	frappe.db.commit()
	return {"created": created, "skipped": skipped}
