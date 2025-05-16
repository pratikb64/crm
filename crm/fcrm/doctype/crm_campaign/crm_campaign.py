# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.email.doctype.email_group.email_group import add_subscribers
from frappe.model.document import Document


class CRMCampaign(Document):
	def after_insert(self):
		if self.status == "Active":
			execute_campaigns()

	def on_update(self):
		if self.status == "Active":
			execute_campaigns()

	@staticmethod
	def default_list_data():
		columns = [
			{
				"label": "Name",
				"type": "Data",
				"key": "campaign_name",
				"width": "12rem",
			},
			{
				"label": "Last Modified",
				"type": "Datetime",
				"key": "modified",
				"width": "8rem",
			},
		]
		rows = [
			"name",
			"campaign_name",
			"modified",
		]
		return {"columns": columns, "rows": rows}

	def execute_campaign(self):
		activities = json.loads(self.activity_list) if self.activity_list else []
		for activity in activities:
			if activity["date"] == frappe.utils.nowdate() and activity["status"] == "Pending":
				print("@@@@@@@@@@@@@@@@@@@@@ activity", activity)

				self.execute_activity(activity)
				activity["status"] = "Completed"
				print("@@@@@@@@@@@@@@@@@@@@@ activities", activities)
				campaign = frappe.get_doc("CRM Campaign", self.name)
				campaign.activity_list = json.dumps(activities)
				print("W@@@@@@@@@@@ cmpaign updated", campaign.activity_list)
				campaign.save()

	def execute_activity(self, activity):
		campaign = self.as_dict()

		email_group = frappe.new_doc("Email Group")
		email_group.title = f"{campaign['name']}-{frappe.generate_hash(length=5)}"
		email_group.save()

		contacts = []
		for contact in campaign["audience"]:
			contacts.append(contact["email"])
		add_subscribers(email_group.name, contacts)

		# email_account = frappe.get_all("Email Account", filters={"default_outgoing": 1})
		# email_account = frappe.get_doc("Email Account", email_account[0]["name"])

		email_template = frappe.get_doc("Email Template", activity["activity"]["data"])
		message = email_template.get_formatted_response(json.loads(self.as_json()))

		newsletter = frappe.new_doc("Newsletter")
		newsletter.update(
			{
				"subject": campaign["subject"],
				"message": message,
				"email_group": [{"email_group": email_group.name}],
				"sender_email": campaign["sender_email"],
				"sender_name": campaign["sender_name"],
			}
		)
		newsletter.save()
		newsletter.send_emails()


def execute_campaigns():
	campaigns = frappe.get_all("CRM Campaign", filters={"status": "Active"})
	for doc in campaigns:
		full_doc = frappe.get_doc("CRM Campaign", doc.name)
		full_doc.execute_campaign()
	return
