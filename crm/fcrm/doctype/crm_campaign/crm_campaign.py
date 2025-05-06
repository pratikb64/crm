# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CRMCampaign(Document):
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
	pass
