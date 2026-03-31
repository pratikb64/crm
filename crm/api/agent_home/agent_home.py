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
			if chart['chart'] == 'funnel_conversion' and chart.get('selected_statuses'):
				chart["data"] = method(statuses=chart.get('selected_statuses'))
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
def get_upcoming_activities(ticket_type: str = "upcoming_sla"):
	user = frappe.session.user
	Lead = DocType("CRM Lead")
	limit = 6

	if ticket_type == "upcoming_sla":
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
				"type": "upcoming_sla",
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

	elif ticket_type == "new_leads":
		# Leads assigned to current user in the last 24 hours
		one_day_ago = frappe.utils.add_to_date(frappe.utils.now_datetime(), hours=-24)
		leads = (
			frappe.qb.from_(Lead)
			.select(
				Lead.name,
				Lead.lead_name.as_("subject"),
				Lead.status,
				Lead.source.as_("agent_group"),
				Lead.annual_revenue.as_("priority"),
				Lead.annual_revenue.as_("priority_integer_value"),
				Lead.creation,
			)
			.where(Lead.lead_owner == user)
			.where(Lead.converted == 0)
			.where(Lead.creation >= one_day_ago)
			.orderby(Lead.creation, order=frappe.qb.desc)
			.limit(limit)
			.run(as_dict=True)
		)

		for lead in leads:
			lead["reason"] = {
				"type": "new_leads",
				"text": "Recently assigned",
			}

		total_count = (
			frappe.qb.from_(Lead)
			.select(Count(Lead.name).as_("cnt"))
			.where(Lead.lead_owner == user)
			.where(Lead.converted == 0)
			.where(Lead.creation >= one_day_ago)
			.run(as_dict=True)
		)
		total = total_count[0]["cnt"] if total_count else 0

	elif ticket_type == "pending":
		# Leads the user owns that have not been responded to (first_responded_on is null)
		leads = (
			frappe.qb.from_(Lead)
			.select(
				Lead.name,
				Lead.lead_name.as_("subject"),
				Lead.status,
				Lead.source.as_("agent_group"),
				Lead.annual_revenue.as_("priority"),
				Lead.annual_revenue.as_("priority_integer_value"),
				Lead.creation,
				Lead.communication_status,
			)
			.where(Lead.lead_owner == user)
			.where(Lead.converted == 0)
			.where(Lead.first_responded_on.isnull())
			.orderby(Lead.creation)
			.limit(limit)
			.run(as_dict=True)
		)

		for lead in leads:
			time_ago = _format_time_ago(lead.get("creation"))
			lead["reason"] = {
				"type": "pending",
				"text": f"Pending for {time_ago}",
			}

		total_count = (
			frappe.qb.from_(Lead)
			.select(Count(Lead.name).as_("cnt"))
			.where(Lead.lead_owner == user)
			.where(Lead.converted == 0)
			.where(Lead.first_responded_on.isnull())
			.run(as_dict=True)
		)
		total = total_count[0]["cnt"] if total_count else 0

	else:
		leads = []
		total = 0

	min_priority, max_priority = _get_priority_range()

	return {
		"leads": leads,
		"total_pending_leads": total,
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
def get_deals_by_stage():
	"""
	Returns deals grouped by status with total deal value.
	[{label: 'Prospecting', value: 12000}, ...]
	"""
	CRMDeal = DocType("CRM Deal")
	CRMDealStatus = DocType("CRM Deal Status")

	result = (
		frappe.qb.from_(CRMDeal)
		.join(CRMDealStatus)
		.on(CRMDeal.status == CRMDealStatus.name)
		.select(
			CRMDeal.status.as_("label"),
			Sum(IfNull(CRMDeal.deal_value, 0) * IfNull(CRMDeal.exchange_rate, 1)).as_("value"),
		)
		.where(CRMDealStatus.type.notin(["Lost"]))
		.groupby(CRMDeal.status)
		.run(as_dict=True)
	)

	# Return only label + value for the chart component
	return [{"label": r["label"], "value": round(r["value"] or 0, 2)} for r in result]


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
			Sum(
				IfNull(CRMDeal.deal_value, 0) * IfNull(CRMDeal.exchange_rate, 1)
			).as_("actual"),
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
			Sum(
				IfNull(CRMDeal.expected_deal_value, 0) * IfNull(CRMDeal.exchange_rate, 1)
			).as_("projected"),
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
	Returns monthly forecasted vs actual revenue for the last 6 months.
	Compatible with ForecastVsActual.vue's defaultData shape:
	{categories: [...], forecast: [...], actual: [...]}
	"""
	CRMDeal = DocType("CRM Deal")
	CRMDealStatus = DocType("CRM Deal Status")

	# Last 6 months
	six_months_ago = frappe.utils.add_months(frappe.utils.nowdate(), -6)
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
		.where(CRMDeal.expected_closure_date >= six_months_ago)
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

	# Generate all months in the last 6 months (inclusive)
	categories = []
	forecast = []
	actual = []

	today_dt = frappe.utils.get_datetime(today)
	for i in range(5, -1, -1):
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
