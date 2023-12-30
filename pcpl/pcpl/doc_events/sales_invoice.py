import frappe
from pcpl.pcpl.doctype.sales_secondary.sales_secondary import get_price_list_rate_for
from frappe.utils import flt

def on_submit(self, method):
    if self.due_date < self.posting_date:
        frappe.throw("Due Date can not be before posting date.")
    for d in self.get("items"):
        if(d.item_tax_template == "CGST AND SGST 18 %"):
            if(d.gst_amount != (d.amount * 0.18)):
                frappe.throw("GST Amount is Invalid")
        if(d.item_tax_template == "CGST AND SGST 28 %"):
            if(d.gst_amount != (d.amount * 0.28)):
                frappe.throw("GST Amount is Invalid")
        if(d.item_tax_template == "CGST AND SGST 12 %"):
            if(d.gst_amount != (d.amount * 0.12)):
                frappe.throw("GST Amount is Invalid")
        if(d.item_tax_template == "CGST AND SGST 5 %"):
            if(d.gst_amount != (d.amount * 0.05)): 
                frappe.throw("GST Amount is Invalid")
        if(d.item_tax_template == "CGST AND SGST 0.1 %"):
            if(d.gst_amount != (d.amount * 0.001)): 
                frappe.throw("GST Amount is Invalid")
        if(d.item_tax_template == "CGST AND SGST 0 %"):
            if(d.gst_amount != (d.amount * 0)): 
                frappe.throw("GST Amount is Invalid")
        if(d.item_tax_template == "IGST 12% Export - PC"):
            if(d.gst_amount != (d.amount * 0.12)): 
                frappe.throw("GST Amount is Invalid")
        if(d.item_tax_template == "IGST 18% Export - PC"):
            if(d.gst_amount != (d.amount * 0.18)): 
                frappe.throw("GST Amount is Invalid")
        if(d.item_tax_template == "IGST 18 %"):
            if(d.gst_amount != (d.amount * 0.18)): 
                frappe.throw("GST Amount is Invalid")
        if(d.item_tax_template == "IGST 28 %"):
            if(d.gst_amount != (d.amount * 0.28)): 
                frappe.throw("GST Amount is Invalid")
        if(d.item_tax_template == "IGST 12 %"):
            if(d.gst_amount != (d.amount * 0.12)): 
                frappe.throw("GST Amount is Invalid")
        if(d.item_tax_template == "IGST 5 %"):
            if(d.gst_amount != (d.amount * 0.05)): 
                frappe.throw("GST Amount is Invalid")
        if(d.item_tax_template == "IGST 0.1 %"):
            if(d.gst_amount != (d.amount * 0.001)): 
                frappe.throw("GST Amount is Invalid")
        if(d.item_tax_template == "IGST 0 %"):
            if(d.gst_amount != (d.amount * 0)): 
                frappe.throw("GST Amount is Invalid")

    validate_rate(self)

def validate(self, method):
    if(self.invoice_for_free_item == 1):
        for row in self.items:
            if not row.get('free_item_pricelist_rate') or row.get('free_item_pricelist_rate') == 0:
                row.free_item_pricelist_rate = get_price_list_rate_for(row.item_code,self.selling_price_list,row.uom,self.posting_date)
    
    if self.territory:
        territory_doc = frappe.get_doc('Territory' , self.territory)
        if territory_doc.parent_territory:
            zone = frappe.db.get_value('Territory' , territory_doc.parent_territory , 'parent_territory')
            if zone:
                self.zone = zone
    # for i in self.get("items"):
    #     if(i.gst_amount != (i.amount * 0.18)):
    #         frappe.throw("GST Amount is Invalid")

    # As per discuss with Sagar Patel removed this validation
    # if(self.naming_series != 'SI-O-2223-.####'):
    # 	if(self.invoice_for_free_item == 1):
    # 		for i in self.items:
    # 			if(i.free_item == 0):
    # 				frappe.throw(
    # 					title='Error',
    # 					msg=f"Row No {i.item_code} Should be free"
    # 					)
    # 		if(self.total > 0):
    # 			frappe.throw("Net Total Shuld be Zero")
    # 	else:
    # 		for i in self.items:
    # 			if(i.free_item==1):
    # 				frappe.throw(
    # 					title='Error',
    # 					msg=f"Row No {i.item_code} Should not be free"
    # 					)
def before_validate(self,method):
    for d in self.get('items'):
        if(d.price_list_rate != 0):
            d.gross_amount = d.qty * d.price_list_rate
        if(d.gross_amount != 0):
            d.discount_amount_total = (flt(d.gross_amount) * flt(d.discount_percentage))/100
        if(d.item_tax_template == "CGST AND SGST 18 %"):
            d.gst_amount = d.amount * 0.18
        if(d.item_tax_template == "CGST AND SGST 28 %"):
            d.gst_amount = d.amount * 0.28
        if(d.item_tax_template == "CGST AND SGST 12 %"):
            d.gst_amount = d.amount * 0.12
        if(d.item_tax_template == "CGST AND SGST 5 %"):
            d.gst_amount = d.amount * 0.05
        if(d.item_tax_template == "CGST AND SGST 0.1 %"):
            d.gst_amount = d.amount * 0.001
        if(d.item_tax_template == "CGST AND SGST 0 %"):
            d.gst_amount = d.amount * 0  
        if(d.item_tax_template == "IGST 12% Export - PC"):
            d.gst_amount = d.amount * 0.12
        if(d.item_tax_template == "IGST 18% Export - PC"):
            d.gst_amount = d.amount * 0.18
        if(d.item_tax_template == "IGST 18 %"):
            d.gst_amount = d.amount * 0.18
        if(d.item_tax_template == "IGST 28 %"):
            d.gst_amount = d.amount * 0.28
        if(d.item_tax_template == "IGST 12 %"):
            d.gst_amount = d.amount * 0.12
        if(d.item_tax_template == "IGST 5 %"):
            d.gst_amount = d.amount * 0.05
        if(d.item_tax_template == "IGST 0.1 %"):
            d.gst_amount = d.amount * 0.001
        if(d.item_tax_template == "IGST 0 %"):
            d.gst_amount = d.amount * 0 
        if not d.item_tax_template:
            d.gst_amount = 0
    
        d.net_amount_total = d.amount + d.gst_amount
def before_save(self, method):
    set_income_account(self)

def before_submit(self, method):
    tax_validation(self)

def set_income_account(self):
    if self.income_account:
        for row in self.items:
            row.income_account = self.income_account

def tax_validation(self):
    if self.gst_category and self.gst_category == "Registered Regular" and not self.is_return and self.total_taxes_and_charges <= 0 and not self.invoice_for_free_item and not self.is_exempted:
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

def validate_rate(self):
    rate_diff_list = []
    gst_amount_diff_list = []
    for row in self.items:
        if row.discount_percentage == 0 and row.price_list_rate != row.rate:
            rate_diff_list.append(row.item_code)
    
        if not row.free_item and row.get('gst_amount') == 0  and row.get('gross_amount') == 0:
            gst_amount_diff_list.append(row.item_code)
    if rate_diff_list:
        frappe.throw(f"There is rate difference in following items : {', '.join(rate_diff_list)}")

    if gst_amount_diff_list:
        frappe.throw(f"Gst amount and Gross amount can not be zero in following Item : {', '.join(gst_amount_diff_list)}")