from frappe import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count


def get_default_agent_dashboard():
	return '[{"chart":"revenue_performance","layout":{"x":30,"y":51,"w":30,"h":31,"minW":30,"minH":31}},{"chart":"expected_closure","layout":{"x":40,"y":32,"w":20,"h":19,"minW":20,"minH":19}},{"chart":"deals_by_stage","layout":{"x":0,"y":32,"w":20,"h":19,"minW":20,"minH":19}},{"chart":"top_open_deals","layout":{"x":20,"y":32,"w":20,"h":19,"minW":20,"minH":19}},{"chart":"funnel_conversion","layout":{"x":0,"y":51,"w":30,"h":31}},{"chart":"upcoming_activities","layout":{"x":0,"y":0,"w":60,"h":32}}]'


def calculate_percentage_change(current_value: float, previous_value: float) -> float:
	"""
	Calculate the percentage change between two values.
	Returns 999 when there's no previous value but there is a current value.
	Returns 0 when both values are zero.
	"""
	if previous_value > 0:
		return round(((current_value - previous_value) / previous_value) * 100, 2)
	elif current_value > 0:
		return 999
	return 0


def get_priority_range():
	CRMLead = DocType("CRM Lead")
	result = (
		frappe.qb.from_(CRMLead)
		.select(
			CRMLead.annual_revenue,
		)
		.where(CRMLead.annual_revenue.isnotnull())
		.run(as_dict=True)
	)
	if result:
		values = [r["annual_revenue"] for r in result if r["annual_revenue"]]
		if values:
			return min(values), max(values)
	return 0, 0


def get_deal_priority_range():
	CRMDeal = DocType("CRM Deal")
	result = (
		frappe.qb.from_(CRMDeal)
		.select(
			CRMDeal.expected_deal_value,
		)
		.where(CRMDeal.expected_deal_value.isnotnull())
		.run(as_dict=True)
	)
	if result:
		values = [r["expected_deal_value"] for r in result if r["expected_deal_value"]]
		if values:
			return min(values), max(values)
	return 0, 0


def get_count(query_builder):
	"""Extract count from a query builder that already has WHERE clauses applied."""
	count_result = query_builder.select(Count("*").as_("cnt")).run(as_dict=True)
	return count_result[0]["cnt"] if count_result else 0
