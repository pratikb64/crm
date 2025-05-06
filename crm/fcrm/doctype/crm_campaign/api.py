import frappe

from crm.api.doc import get_fields_meta
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script


@frappe.whitelist()
def get_campaign(name):
	campaign = frappe.get_doc("CRM Campaign", name)
	campaign.check_permission("read")

	campaign = campaign.as_dict()

	campaign["fields_meta"] = get_fields_meta("CRM Campaign")
	campaign["_form_script"] = get_form_script("CRM Campaign")
	return campaign
