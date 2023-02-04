import frappe
from erpnext.controllers.queries import get_fields, get_filters_cond, get_match_cond

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_delivery_notes_to_be_billed(doctype, txt, searchfield, start, page_len, filters, as_dict):
	fields = get_fields("Delivery Note", ["name", "customer", "posting_date"])

	return frappe.db.sql(
		"""
		select %(fields)s
		from `tabDelivery Note`
		where `tabDelivery Note`.`%(key)s` like %(txt)s and
			`tabDelivery Note`.docstatus = 1
			and status not in ("Stopped", "Closed") %(fcond)s
			and (
				(`tabDelivery Note`.is_return = 0)
				or (`tabDelivery Note`.grand_total = 0)
				or (
					`tabDelivery Note`.is_return = 1
					and return_against in (select name from `tabDelivery Note`)
				)
			)
			%(mcond)s order by `tabDelivery Note`.`%(key)s` asc limit %(start)s, %(page_len)s
	"""
		% {
			"fields": ", ".join(["`tabDelivery Note`.{0}".format(f) for f in fields]),
			"key": searchfield,
			"fcond": get_filters_cond(doctype, filters, []),
			"mcond": get_match_cond(doctype),
			"start": start,
			"page_len": page_len,
			"txt": "%(txt)s",
		},
		{"txt": ("%%%s%%" % txt)},
		as_dict=as_dict,
	)

@frappe.whitelist()
def get_sales_tax_template(tax_category, company):
	return frappe.db.get_value("Sales Taxes and Charges Template", {'tax_category' : tax_category, 'company': company, 'disabled': 0}, 'name')

def set_sales_taxes_and_charges(self, method):
	if self.tax_category and not self.taxes_and_charges:
		self.taxes_and_charges = get_sales_tax_template(self.tax_category, self.company)