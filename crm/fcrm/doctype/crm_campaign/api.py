import frappe

from crm.api.doc import get_fields_meta
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script
from frappe.email.doctype.email_template.email_template import get_email_template
from frappe.core.doctype.communication.email import make


@frappe.whitelist()
def get_campaign(name):
	campaign = frappe.get_doc("CRM Campaign", name)
	campaign.check_permission("read")

	campaign = campaign.as_dict()

	campaign["fields_meta"] = get_fields_meta("CRM Campaign")
	campaign["_form_script"] = get_form_script("CRM Campaign")
	return campaign


@frappe.whitelist()
def send():
	template = get_email_template("Test", {"doc": {}})
	message = frappe.render_template(template, {"doc": {}})
	make(
		recipients="recipient@example.com",
		subject=template.subject,
		content=message,
		send_email=True,
	)
	return "send"
