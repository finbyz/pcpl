import frappe
from pcpl.pcpl.doctype.sales_secondary.sales_secondary import get_price_list_rate_for

def validate(self, method):
	if(self.invoice_for_free_item == 1):
		for row in self.items:
			if not row.free_item_pricelist_rate or row.free_item_pricelist_rate == 0:
				row.free_item_pricelist_rate = get_price_list_rate_for(row.item_code,self.selling_price_list,row.uom,self.posting_date)
	if(self.invoice_for_free_item == 1):
		for i in self.items:
			if(i.free_item == 0):
				frappe.throw(
					 title='Error',
					 msg=f"Row No {i.item_code} Should be free"
					)
		if(self.total > 0):
			frappe.throw("Net Total Shuld be Zero")
	else:
		for i in self.items:
			if(i.free_item==1):
				frappe.throw(
					 title='Error',
					 msg=f"Row No {i.item_code} Should not be free"
					)

def before_save(self, method):
	set_income_account(self)

def before_submit(self, method):
	tax_validation(self)

def set_income_account(self):
	if self.income_account:
		for row in self.items:
			row.income_account = self.income_account

def tax_validation(self):
	if self.gst_category and self.gst_category == "Registered Regular" and not self.is_return and self.total_taxes_and_charges <= 0 and not self.invoice_for_free_item:
		frappe.throw("Taxes has not applied.")

#override from finbyzerp
def validate_einvoice_fields(doc):
	invoice_eligible = validate_eligibility(doc)

	if not invoice_eligible:
		return

	# Finbyz Changes Start: dont change posting date and sales taxes and charges table after irn generated
	if doc.irn and doc.docstatus == 0:
		doc.set_posting_time = 1
		if str(doc.posting_date) != str(frappe.db.get_value("Sales Invoice",doc.name,"posting_date")):
			frappe.throw(_('You cannot edit the invoice after generating IRN'), title=_('Edit Not Allowed'))
		if str(len(doc.taxes)) != str(len(frappe.db.get_all("Sales Taxes and Charges",{'parent':doc.name,'parenttype':doc.doctype}))):
			frappe.throw(_('You cannot edit the invoice after generating IRN'), title=_('Edit Not Allowed'))
	# Finbyz Changes End
	if doc.docstatus == 0 and doc._action == 'save':
		if doc.irn and not doc.eway_bill_cancelled and doc.grand_total != frappe.db.get_value("Sales Invoice",doc.name,"grand_total"):# Finbyz Changes:
			frappe.throw(_('You cannot edit the invoice after generating IRN'), title=_('Edit Not Allowed'))
		if len(doc.name) > 16:
			raise_document_name_too_long_error()

	elif doc.docstatus == 1 and doc._action == 'submit' and not doc.irn and doc.irn_cancelled == 0 and doc.total != 0: #  
		frappe.throw(_('You must generate IRN before submitting the document.'), title=_('Missing IRN'))

	elif doc.irn and doc.docstatus == 2 and doc._action == 'cancel' and not doc.irn_cancelled:
		frappe.throw(_('You must cancel IRN before cancelling the document.'), title=_('Cancel Not Allowed'))