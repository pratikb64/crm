# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CRMAudience(Document):
	@staticmethod
	def default_list_data():
		columns = [
			{
				"label": "First Name",
				"type": "Data",
				"key": "first_name",
				"width": "8rem",
			},
			{
				"label": "Last Name",
				"type": "Data",
				"key": "last_name",
				"width": "8rem",
			},
			{
				"label": "Email",
				"type": "Data",
				"key": "email",
				"width": "10rem",
			},
			{
				"label": "Phone",
				"type": "Data",
				"key": "phone",
				"width": "10rem",
			},
			{
				"label": "Source",
				"type": "Data",
				"key": "source",
				"width": "8rem",
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
			"first_name",
			"last_name",
			"email",
			"phone",
			"source",
			"modified",
		]
		return {"columns": columns, "rows": rows}
