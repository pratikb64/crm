import frappe

from crm.api.doc import get_fields_meta
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script


@frappe.whitelist()
def get_audience(name):
	audience = frappe.get_doc("CRM Audience", name)
	audience.check_permission("read")

	audience = audience.as_dict()

	audience["fields_meta"] = get_fields_meta("CRM Audience")
	audience["_form_script"] = get_form_script("CRM Audience")
	return audience
