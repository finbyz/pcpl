
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{"label": _("Invoice No"), "fieldname": "invoice_no", "fieldtype": "Link", "options": "Sales Invoice", "width": 130},
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
		{"label": _("Zone"), "fieldname": "zone", "fieldtype": "Link", "options": "Customer Group", "width": 100},
		{"label": _("Devision"), "fieldname": "devision", "fieldtype": "Link", "options": "Customer Group", "width": 100},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
		{"label": _("City"), "fieldname": "customer_city", "fieldtype": "Data", "width": 100},
		{"label": _("State"), "fieldname": "place_of_supply", "fieldtype": "Data", "width": 100},
		{"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 130},
		{"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 130},
		{"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 130},
		{"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 80},
		{"label": _("Price List Rate"), "fieldname": "price_list_rate", "fieldtype": "Currency", "width": 100},
		{"label": _("Gross Amount"), "fieldname": "gross_amount", "fieldtype": "Currency", "width": 100},
		{"label": _("Discount"), "fieldname": "discount_percentage", "fieldtype": "Percent", "width": 100},
		{"label": _("Discount Amt"), "fieldname": "discount_amount_total", "fieldtype": "Currency", "width": 100},
		{"label": _("Net Amount"), "fieldname": "base_net_amount", "fieldtype": "Currency", "width": 100},
		{"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 100},
		{"label": _("Parcel"), "fieldname": "total_parcel", "fieldtype": "Data", "width": 100},
		{"label": _("Transporter"), "fieldname": "transporter", "fieldtype": "Link", "options": "Supplier", "width": 140},
		{"label": _("LR No"), "fieldname": "lr_no", "fieldtype": "Data", "width": 100},
		{"label": _("LR Date"), "fieldname": "lr_date", "fieldtype": "Data", "width": 100},
		{"label": _("POD"), "fieldname": "pod_number", "fieldtype": "Data", "width": 100},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
	]
	return columns

def get_data(filters):
	conditions = ""
	if filters.get("invoice_no"):
		conditions += f""" and si.name = '{filters.get("invoice_no")}'"""
	
	if filters.get("customer"):
		conditions += f""" and si.customer = '{filters.get("customer")}'"""

	if filters.get("status"):
		conditions += " and si.status in %(status)s"

	if filters.get("item_code"):
		conditions += f""" and si_item.item_code = '{filters.get("item_code")}'"""

	if filters.get("zone"):
		conditions += f""" and customer_g.parent_customer_group = '{filters.get("zone")}'"""

	if filters.get("devision"):
		conditions += f""" and customer_g.name = '{filters.get("devision")}'"""

	if filters.get("from_date"):
		conditions += f""" and si.posting_date >= '{filters.get("from_date")}'"""

	if filters.get("to_date"):
		conditions += f""" and si.posting_date <= '{filters.get("to_date")}'"""

	data = frappe.db.sql("""
		select
			si.name as invoice_no, si.posting_date, customer_g.parent_customer_group as zone, customer_g.name as devision,
			si.customer, si.customer_city, si.place_of_supply, si_item.item_code, si_item.item_name,si_item.item_group, si_item.qty,
			si_item.price_list_rate, (si_item.price_list_rate * si_item.qty) as gross_amount, si_item.discount_percentage,
			si_item.discount_amount_total, si_item.base_net_amount, round(si_item.net_amount_total, 0) as grand_total,
			si.total_parcel, si.transporter, si.lr_no, si.lr_date, si.pod_number, si.status
		from
			`tabSales Invoice Item` as si_item
			JOIN `tabSales Invoice` as si on si.name = si_item.parent
			JOIN `tabCustomer` as customer on customer.name = si.customer
			JOIN `tabCustomer Group` as customer_g on customer_g.name = customer.customer_group
		where
			si.docstatus != 2 {conditions}
		order by posting_date desc
	""".format(conditions=conditions), (filters), as_dict= True)

	return data
