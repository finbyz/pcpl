
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
		
		{"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 130},
		{"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 130},
		{"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 80},
		{"label": _("Price List Rate"), "fieldname": "rate", "fieldtype": "Currency", "width": 100},
		{"label": _("Gross Amount"), "fieldname": "gross_amount", "fieldtype": "Currency", "width": 100},
		# {"label": _("Discount"), "fieldname": "discount_percentage", "fieldtype": "Percent", "width": 100},
		# {"label": _("Discount Amt"), "fieldname": "discount_amount_total", "fieldtype": "Currency", "width": 100},
		# {"label": _("Net Amount"), "fieldname": "base_net_amount", "fieldtype": "Currency", "width": 100},
		# {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 100},
		# {"label": _("Parcel"), "fieldname": "total_parcel", "fieldtype": "Data", "width": 100},
		# {"label": _("Transporter"), "fieldname": "transporter", "fieldtype": "Link", "options": "Supplier", "width": 140},
		# {"label": _("LR No"), "fieldname": "lr_no", "fieldtype": "Data", "width": 100},
		# {"label": _("LR Date"), "fieldname": "lr_date", "fieldtype": "Data", "width": 100},
		# {"label": _("POD"), "fieldname": "pod_number", "fieldtype": "Data", "width": 100},
		# {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
	]
	
	return columns

def get_data(filters):
	conditions = ""
	if filters.get("invoice_no"):
		conditions += f""" and ss.name = '{filters.get("invoice_no")}'"""
	if filters.get("customer"):
		conditions += f""" and ss.secondary_party = '{filters.get("customer")}'"""
	if filters.get("item_code"):
		conditions += f""" and ssi.item_code = '{filters.get("item_code")}'"""
	if filters.get("zone"):
		conditions += f""" and ss.zone= '{filters.get("zone")}'"""
	if filters.get("devision"):
		conditions += f""" and ss.executive = '{filters.get("devision")}'"""
	if filters.get("cn"):
		conditions+=f""" and ss.cn='{filters.get("cn")}'"""
	if filters.get("transfer_cn"):
		conditions+=f""" and ss.transfer_cn='{filters.get("transfer_cn")}'"""
	if filters.get("from_date"):
		conditions += f""" and ss.posting_date >= '{filters.get("from_date")}'"""
	if filters.get("to_date"):
		conditions += f"""and ss.posting_date <= '{filters.get("to_date")}'"""
	
	lft,rgt=frappe.db.get_value("Territory",{'is_group':1,'is_secondary_':1,'territory_type':None},['lft','rgt'])
	
	data = frappe.db.sql("""
		select
			ss.name as invoice_no, ss.posting_date, ss.zone as zone, ss.executive as devision,
			ss.secondary_party as customer, ss.territory as customer_city,ssi.item_code, ssi.item_name, ssi.qty,
			ssi.rate, (ssi.rate * ssi.qty) as gross_amount
		from
			`tabSales Secondary Item` as ssi
			LEFT join  `tabSales Secondary` as ss on ss.name=ssi.parent
			LEFT join `tabCustomer` as customer on customer.name = ss.secondary_party
			LEFT join `tabCustomer Group` as customer_g on customer_g.name = customer.customer_group
			
			
			
		where
			customer_g.is_secondary_group=1 {conditions} 
		order by posting_date desc
	""".format(conditions=conditions,lft=lft,rgt=rgt), (filters), as_dict= True)
	
	return data
	