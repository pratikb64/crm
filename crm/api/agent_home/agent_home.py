import json

import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count, Date, DateFormat, IfNull, Sum


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


def _get_priority_range():
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


def _get_deal_priority_range():
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


def _format_time_ago(dt):
	"""Return a human-readable 'X ago' string for a datetime."""
	if not dt:
		return ""
	now = frappe.utils.now_datetime()
	if isinstance(dt, str):
		dt = frappe.utils.get_datetime(dt)
	diff = now - dt
	seconds = int(diff.total_seconds())
	if seconds < 60:
		return f"{seconds}s ago"
	elif seconds < 3600:
		return f"{seconds // 60}m ago"
	elif seconds < 86400:
		return f"{seconds // 3600}h ago"
	else:
		return f"{seconds // 86400}d ago"


def _format_time_until(dt):
	"""Return a human-readable 'X' string for time until a deadline."""
	if not dt:
		return "unknown"
	now = frappe.utils.now_datetime()
	if isinstance(dt, str):
		dt = frappe.utils.get_datetime(dt)
	diff = dt - now
	if diff.total_seconds() < 0:
		return "overdue"
	seconds = int(diff.total_seconds())
	if seconds < 60:
		return f"{seconds}s"
	elif seconds < 3600:
		return f"{seconds // 60}m"
	elif seconds < 86400:
		return f"{seconds // 3600}h"
	else:
		return f"{seconds // 86400}d"


@frappe.whitelist()
def get_dashboard(reset_layout: bool = False):
	dashboard = frappe.db.exists("CRM Dashboard", {"owner": frappe.session.user})
	dashboard_id = None

	if not dashboard:
		layout = json.loads(get_default_agent_dashboard())
	else:
		dashboard = frappe.db.get_value(
			"CRM Dashboard",
			{"owner": frappe.session.user},
			["name", "layout"],
		)
		if reset_layout:
			layout = json.loads(get_default_agent_dashboard())
		else:
			layout = json.loads(dashboard[1])
		dashboard_id = dashboard[0]

	for chart in layout:
		method_name = f"get_{chart['chart']}"
		if hasattr(frappe.get_attr("crm.api.agent_home.agent_home"), method_name):
			method = getattr(frappe.get_attr("crm.api.agent_home.agent_home"), method_name)
			# Pass selected_statuses for funnel conversion chart
			if chart["chart"] == "funnel_conversion" and chart.get("selected_statuses"):
				chart["data"] = method(statuses=chart.get("selected_statuses"))
			else:
				chart["data"] = method()
		else:
			chart["data"] = None

	return {
		"layout": layout,
		"default_layout": get_default_agent_dashboard(),
		"dashboard_id": dashboard_id,
	}


@frappe.whitelist()
def get_upcoming_activities(activity_type: str = "leads"):
	user = frappe.session.user
	limit = 6

	if activity_type == "leads":
		return _get_upcoming_leads(user, limit)
	elif activity_type == "deals":
		return _get_upcoming_deals(user, limit)
	elif activity_type == "tasks":
		return _get_upcoming_tasks(user, limit)
	else:
		return {"activities": [], "total": 0, "min_priority": 0, "max_priority": 0}


def _get_upcoming_leads(user, limit):
	Lead = DocType("CRM Lead")
	# Leads with an upcoming SLA response deadline
	leads = (
		frappe.qb.from_(Lead)
		.select(
			Lead.name,
			Lead.lead_name.as_("subject"),
			Lead.status,
			Lead.source.as_("agent_group"),
			Lead.annual_revenue.as_("priority"),
			Lead.annual_revenue.as_("priority_integer_value"),
			Lead.response_by,
			Lead.sla_status,
		)
		.where(Lead.lead_owner == user)
		.where(Lead.converted == 0)
		.where(Lead.response_by.isnotnull())
		.where(Lead.sla_status.isin(["First Response Due", "Resolution Due"]))
		.orderby(Lead.response_by)
		.limit(limit)
		.run(as_dict=True)
	)

	for lead in leads:
		due_time = lead.get("response_by")
		time_until = _format_time_until(due_time)
		lead["reason"] = {
			"type": "leads",
			"text": f"Response due in {time_until}" if time_until != "overdue" else "Response overdue",
		}

	# Count for "see all"
	total_count = (
		frappe.qb.from_(Lead)
		.select(Count(Lead.name).as_("cnt"))
		.where(Lead.lead_owner == user)
		.where(Lead.converted == 0)
		.where(Lead.response_by.isnotnull())
		.where(Lead.sla_status.isin(["First Response Due", "Resolution Due"]))
		.run(as_dict=True)
	)
	total = total_count[0]["cnt"] if total_count else 0
	min_priority, max_priority = _get_priority_range()

	return {
		"activities": leads,
		"total": total,
		"min_priority": min_priority,
		"max_priority": max_priority,
	}


def _get_upcoming_deals(user, limit):
	Deal = DocType("CRM Deal")
	CRMDealStatus = DocType("CRM Deal Status")

	# Deals with SLA response due or expected closure in near future
	deals = (
		frappe.qb.from_(Deal)
		.join(CRMDealStatus)
		.on(Deal.status == CRMDealStatus.name)
		.select(
			Deal.name,
			Deal.organization.as_("subject"),
			CRMDealStatus.deal_status.as_("status"),
			Deal.source.as_("agent_group"),
			Deal.expected_deal_value.as_("priority"),
			Deal.expected_deal_value.as_("priority_integer_value"),
			Deal.response_by,
			Deal.sla_status,
			Deal.expected_closure_date,
		)
		.where(Deal.deal_owner == user)
		.where(CRMDealStatus.type.notin(["Lost", "Won"]))
		.where(
			(Deal.response_by.isnotnull() & Deal.sla_status.isin(["First Response Due", "Resolution Due"]))
			| (
				Deal.expected_closure_date.isnotnull()
				& (Deal.expected_closure_date >= frappe.utils.nowdate())
			)
		)
		.orderby(Deal.response_by)
		.limit(limit)
		.run(as_dict=True)
	)

	for deal in deals:
		if deal.get("response_by") and deal.get("sla_status") in ["First Response Due", "Resolution Due"]:
			due_time = deal.get("response_by")
			time_until = _format_time_until(due_time)
			deal["reason"] = {
				"type": "deals",
				"text": f"Response due in {time_until}" if time_until != "overdue" else "Response overdue",
			}
		elif deal.get("expected_closure_date"):
			due_time = deal.get("expected_closure_date")
			time_until = _format_time_until(due_time)
			deal["reason"] = {
				"type": "deals",
				"text": f"Closing in {time_until}" if time_until != "overdue" else "Closure overdue",
			}

	# Count for "see all"
	total_count = (
		frappe.qb.from_(Deal)
		.join(CRMDealStatus)
		.on(Deal.status == CRMDealStatus.name)
		.select(Count(Deal.name).as_("cnt"))
		.where(Deal.deal_owner == user)
		.where(CRMDealStatus.type.notin(["Lost", "Won"]))
		.where(
			(Deal.response_by.isnotnull() & Deal.sla_status.isin(["First Response Due", "Resolution Due"]))
			| (
				Deal.expected_closure_date.isnotnull()
				& (Deal.expected_closure_date >= frappe.utils.nowdate())
			)
		)
		.run(as_dict=True)
	)
	total = total_count[0]["cnt"] if total_count else 0
	min_priority, max_priority = _get_deal_priority_range()

	return {
		"activities": deals,
		"total": total,
		"min_priority": min_priority,
		"max_priority": max_priority,
	}


def _get_upcoming_tasks(user, limit):
	Task = DocType("CRM Task")

	# Tasks assigned to user that are not done/canceled and have due date
	tasks = (
		frappe.qb.from_(Task)
		.select(
			Task.name,
			Task.title.as_("subject"),
			Task.status,
			Task.priority.as_("agent_group"),
			Task.priority.as_("priority"),
			Task._idx.as_("priority_integer_value"),
			Task.due_date.as_("response_by"),
			Task.reference_doctype,
			Task.reference_docname,
		)
		.where(Task.assigned_to == user)
		.where(Task.status.notin(["Done", "Canceled"]))
		.where(Task.due_date.isnotnull())
		.where(Task.due_date >= frappe.utils.add_to_date(frappe.utils.now_datetime(), days=-1))
		.orderby(Task.due_date)
		.limit(limit)
		.run(as_dict=True)
	)

	priority_map = {"Low": 1, "Medium": 2, "High": 3}
	for task in tasks:
		task["priority_integer_value"] = priority_map.get(task.get("priority"), 0)
		due_time = task.get("response_by")
		time_until = _format_time_until(due_time)
		task["reason"] = {
			"type": "tasks",
			"text": f"Due in {time_until}" if time_until != "overdue" else "Task overdue",
		}
		# Add reference info
		if task.get("reference_doctype") and task.get("reference_docname"):
			task["agent_group"] = f"{task['reference_doctype']}: {task['reference_docname']}"

	# Count for "see all"
	total_count = (
		frappe.qb.from_(Task)
		.select(Count(Task.name).as_("cnt"))
		.where(Task.assigned_to == user)
		.where(Task.status.notin(["Done", "Canceled"]))
		.where(Task.due_date.isnotnull())
		.where(Task.due_date >= frappe.utils.add_to_date(frappe.utils.now_datetime(), days=-1))
		.run(as_dict=True)
	)
	total = total_count[0]["cnt"] if total_count else 0

	# Calculate priority range for tasks
	all_priorities = [priority_map.get(t.get("priority"), 0) for t in tasks if t.get("priority")]
	min_priority = min(all_priorities) if all_priorities else 0
	max_priority = max(all_priorities) if all_priorities else 0

	return {
		"activities": tasks,
		"total": total,
		"min_priority": min_priority,
		"max_priority": max_priority,
	}


@frappe.whitelist()
def get_funnel_conversion(statuses: list | None = None):
	"""
	Returns funnel conversion: leads by status.
	If statuses provided, filter by those statuses, otherwise use default funnel statuses.
	[{label: 'Lead Status Name', value: 385}, ...]
	"""
	from_date = frappe.utils.get_first_day(frappe.utils.nowdate())
	to_date = frappe.utils.get_last_day(frappe.utils.nowdate())

	CRMLead = DocType("CRM Lead")
	CRMLeadStatus = DocType("CRM Lead Status")

	# Default funnel statuses if none provided
	if not statuses:
		statuses = ["New", "Qualified", "Proposal", "Negotiation", "Won"]

	# Get lead counts by status for this month
	lead_counts = (
		frappe.qb.from_(CRMLead)
		.join(CRMLeadStatus)
		.on(CRMLead.status == CRMLeadStatus.name)
		.select(
			CRMLeadStatus.lead_status,
			Count("*").as_("count"),
		)
		.where(Date(CRMLead.creation).between(from_date, to_date))
		.where(CRMLeadStatus.lead_status.isin(statuses))
		.groupby(CRMLeadStatus.lead_status)
		.orderby(CRMLeadStatus.position)
		.run(as_dict=True)
	)

	# Create a dict for easy lookup
	counts_by_status = {row["lead_status"]: row["count"] for row in lead_counts}

	# Return all requested statuses with 0 as default
	result = []
	for status in statuses:
		result.append({"label": status, "value": counts_by_status.get(status, 0)})

	return result


@frappe.whitelist()
def get_lead_statuses():
	"""
	Returns all available lead statuses ordered by position.
	[{label: 'Status Name', value: 'Status Name'}, ...]
	"""
	CRMLeadStatus = DocType("CRM Lead Status")

	statuses = (
		frappe.qb.from_(CRMLeadStatus)
		.select(
			CRMLeadStatus.lead_status,
			CRMLeadStatus.position,
		)
		.orderby(CRMLeadStatus.position)
		.run(as_dict=True)
	)

	return [{"label": status["lead_status"], "value": status["lead_status"]} for status in statuses]


@frappe.whitelist()
def get_funnel_conversion_preferences():
	"""
	Get funnel conversion preferences from CRM Dashboard.
	Returns the selected statuses for funnel conversion chart.
	"""
	dashboard = frappe.db.get_value("CRM Dashboard", {"owner": frappe.session.user}, ["layout"])

	if dashboard:
		try:
			layout = json.loads(dashboard)
			# Find funnel conversion chart and return its preferences
			for chart in layout:
				if chart.get("chart") == "funnel_conversion":
					return chart.get("preferences", {}).get(
						"statuses", ["New", "Qualified", "Proposal", "Negotiation", "Won"]
					)
		except (json.JSONDecodeError, AttributeError):
			pass

	# Return default preferences if no custom ones found
	return ["New", "Qualified", "Proposal", "Negotiation", "Won"]


@frappe.whitelist()
def save_funnel_conversion_preferences(statuses: list):
	"""
	Save funnel conversion preferences to CRM Dashboard.
	"""
	dashboard = frappe.db.get_value("CRM Dashboard", {"owner": frappe.session.user}, ["name", "layout"])

	if not dashboard:
		# Create new dashboard if doesn't exist
		dashboard_doc = frappe.new_doc("CRM Dashboard")
		dashboard_doc.title = f"Dashboard - {frappe.session.user}"
		dashboard_doc.private = 1
		dashboard_doc.user = frappe.session.user
		layout = json.loads(get_default_agent_dashboard())
	else:
		dashboard_name, layout_json = dashboard
		layout = json.loads(layout_json)
		dashboard_doc = frappe.get_doc("CRM Dashboard", dashboard[0])

	# Update funnel conversion chart preferences
	for chart in layout:
		if chart.get("chart") == "funnel_conversion":
			if "preferences" not in chart:
				chart["preferences"] = {}
			chart["preferences"]["statuses"] = statuses
			break

	# Save updated layout
	dashboard_doc.layout = json.dumps(layout)
	dashboard_doc.save(ignore_permissions=True)

	return {"success": True, "statuses": statuses}


@frappe.whitelist()
def get_deal_statuses():
	"""
	Returns all available deal statuses ordered by position.
	[{label: 'Status Name', value: 'Status Name'}, ...]
	"""
	CRMDealStatus = DocType("CRM Deal Status")

	statuses = (
		frappe.qb.from_(CRMDealStatus)
		.select(
			CRMDealStatus.name,
			CRMDealStatus.deal_status,
			CRMDealStatus.position,
		)
		.orderby(CRMDealStatus.position)
		.run(as_dict=True)
	)

	result = [{"label": status["deal_status"], "value": status["name"]} for status in statuses]

	return result


@frappe.whitelist()
def get_deals_by_stage(stages: list | None = None):
	"""
	Returns deals grouped by status with total deal value.
	Always returns top 3 stages by value + Others (even if values are 0).
	[{label: 'Prospecting', value: 12000}, ...]
	"""
	CRMDeal = DocType("CRM Deal")
	CRMDealStatus = DocType("CRM Deal Status")

	# Get all non-Lost deal statuses first
	all_statuses = (
		frappe.qb.from_(CRMDealStatus)
		.select(CRMDealStatus.deal_status)
		.where(CRMDealStatus.type.notin(["Lost"]))
		.orderby(CRMDealStatus.position)
		.run(as_dict=True)
	)
	all_status_names = [s["deal_status"] for s in all_statuses]

	# Get deal values by status
	query = (
		frappe.qb.from_(CRMDeal)
		.join(CRMDealStatus)
		.on(CRMDeal.status == CRMDealStatus.name)
		.select(
			CRMDeal.status.as_("label"),
			Sum(IfNull(CRMDeal.deal_value, 0) * IfNull(CRMDeal.exchange_rate, 1)).as_("value"),
		)
		.where(CRMDealStatus.type.notin(["Lost"]))
	)

	# Filter by specific stages if provided (for backwards compatibility)
	if stages and len(stages) > 0:
		query = query.where(CRMDeal.status.isin(stages))
	result = query.groupby(CRMDeal.status).run(as_dict=True)

	# Create a lookup of values by label
	values_by_status = {r["label"]: round(r["value"] or 0, 2) for r in result}

	# Build complete list with all statuses (including ones with 0 value)
	formatted_result = [
		{"label": status, "value": values_by_status.get(status, 0)} for status in all_status_names
	]

	# Sort by value descending to get top stages
	formatted_result.sort(key=lambda x: x["value"], reverse=True)

	# Always return top 3 + Others (when more than 4 stages exist)
	if len(formatted_result) > 4:
		# Take top 3 and combine the rest as 'Others'
		top_3 = formatted_result[:3]
		others_value = sum(item["value"] for item in formatted_result[3:])
		return [*top_3, {"label": "Others", "value": round(others_value, 2)}]

	# For 4 or fewer stages, still group remaining as Others if there are more than 3
	if len(formatted_result) == 4:
		top_3 = formatted_result[:3]
		others_value = formatted_result[3]["value"]
		return [*top_3, {"label": "Others", "value": round(others_value, 2)}]

	# For 3 or fewer stages, pad with empty stages to always show 4 items (3 + Others)
	while len(formatted_result) < 3:
		formatted_result.append({"label": "-", "value": 0})

	# Add Others with 0 value
	others_value = sum(item["value"] for item in formatted_result[3:]) if len(formatted_result) > 3 else 0
	return formatted_result[:3] + [{"label": "Others", "value": round(others_value, 2)}]


@frappe.whitelist()
def get_expected_closure():
	"""
	Returns actual (won deal revenue) vs projected (expected deal value) for this month.
	{actual: 19200, projected: 24000}
	"""
	from_date = frappe.utils.get_first_day(frappe.utils.nowdate())
	to_date = frappe.utils.get_last_day(frappe.utils.nowdate())
	to_date_plus_one = frappe.utils.add_days(to_date, 1)

	CRMDeal = DocType("CRM Deal")
	CRMDealStatus = DocType("CRM Deal Status")

	# Get actual won deals for this month (based on when they were actually won)
	actual_result = (
		frappe.qb.from_(CRMDeal)
		.join(CRMDealStatus)
		.on(CRMDeal.status == CRMDealStatus.name)
		.select(
			Sum(IfNull(CRMDeal.deal_value, 0) * IfNull(CRMDeal.exchange_rate, 1)).as_("actual"),
		)
		.where(CRMDealStatus.type == "Won")
		.where(CRMDeal.closed_date >= from_date)
		.where(CRMDeal.closed_date < to_date_plus_one)
		.run(as_dict=True)
	)

	# Get projected deals expected to close this month
	projected_result = (
		frappe.qb.from_(CRMDeal)
		.join(CRMDealStatus)
		.on(CRMDeal.status == CRMDealStatus.name)
		.select(
			Sum(IfNull(CRMDeal.expected_deal_value, 0) * IfNull(CRMDeal.exchange_rate, 1)).as_("projected"),
		)
		.where(CRMDealStatus.type.notin(["Lost"]))
		.where(Date(CRMDeal.expected_closure_date).between(from_date, to_date))
		.run(as_dict=True)
	)

	actual = round(actual_result[0]["actual"] or 0, 2) if actual_result else 0
	projected = round(projected_result[0]["projected"] or 0, 2) if projected_result else 0

	# Ensure projected >= actual (projected includes actual won deals)
	if projected < actual:
		projected = actual

	return {"actual": actual, "projected": projected}


@frappe.whitelist()
def get_top_open_deals():
	status = frappe.get_all("CRM Deal Status", filters={"type": ["in", ["Open", "Ongoing"]]}, pluck="name")
	deals = frappe.get_all(
		"CRM Deal",
		filters={"status": ["in", status]},
		fields=["name", "organization", "expected_deal_value"],
		order_by="expected_deal_value desc",
		limit=4,
	)

	colors = ["green", "pink", "red", "blue", "gray"]
	return [
		{
			"name": deal.name,
			"label": deal.organization or deal.name,
			"value": deal.expected_deal_value or 0,
			"color": colors[i % len(colors)],
		}
		for i, deal in enumerate(deals)
	]


@frappe.whitelist()
def get_revenue_performance():
	"""
	Returns monthly forecasted vs actual revenue for the last 12 months.
	Compatible with ForecastVsActual.vue's defaultData shape:
	{categories: [...], forecast: [...], actual: [...]}
	"""
	CRMDeal = DocType("CRM Deal")
	CRMDealStatus = DocType("CRM Deal Status")

	# Last 12 months
	twelve_months_ago = frappe.utils.add_months(frappe.utils.nowdate(), -12)
	today = frappe.utils.nowdate()

	forecasted_value = (
		frappe.qb.terms.Case()
		.when(
			CRMDealStatus.type == "Lost",
			IfNull(CRMDeal.expected_deal_value, 0) * IfNull(CRMDeal.exchange_rate, 1),
		)
		.else_(
			IfNull(CRMDeal.expected_deal_value, 0)
			* IfNull(CRMDeal.probability, 0)
			/ 100
			* IfNull(CRMDeal.exchange_rate, 1)
		)
	)

	actual_value = (
		frappe.qb.terms.Case()
		.when(CRMDealStatus.type == "Won", IfNull(CRMDeal.deal_value, 0) * IfNull(CRMDeal.exchange_rate, 1))
		.else_(0)
	)

	result = (
		frappe.qb.from_(CRMDeal)
		.join(CRMDealStatus)
		.on(CRMDeal.status == CRMDealStatus.name)
		.select(
			DateFormat(CRMDeal.expected_closure_date, "%Y-%m").as_("month"),
			Sum(forecasted_value).as_("forecasted"),
			Sum(actual_value).as_("actual"),
		)
		.where(CRMDeal.expected_closure_date >= twelve_months_ago)
		.where(CRMDeal.expected_closure_date.isnotnull())
		.groupby(DateFormat(CRMDeal.expected_closure_date, "%Y-%m"))
		.orderby(DateFormat(CRMDeal.expected_closure_date, "%Y-%m"))
		.run(as_dict=True)
	)

	# Build a dict keyed by YYYY-MM for easy lookup
	data_by_month = {}
	for row in result:
		data_by_month[row["month"]] = {
			"forecasted": round(row["forecasted"] or 0, 2),
			"actual": round(row["actual"] or 0, 2),
		}

	# Generate all months in the last 12 months (inclusive)
	categories = []
	forecast = []
	actual = []

	today_dt = frappe.utils.get_datetime(today)
	for i in range(11, -1, -1):
		month_dt = frappe.utils.add_months(today_dt, -i)
		key = month_dt.strftime("%Y-%m")
		label = month_dt.strftime("%b")
		categories.append(label)
		month_data = data_by_month.get(key, {})
		forecast.append(month_data.get("forecasted", 0))
		actual.append(month_data.get("actual", 0))

	return {
		"categories": categories,
		"forecast": forecast,
		"actual": actual,
	}
