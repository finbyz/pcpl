import frappe
from pcpl.pcpl.doc_events.sales_invoice import validate_rate

def before_validate(self, method):
	for row in self.items:
		if row.free_item == 1:
			row.price_list_rate = 0
			row.rate = 0
	
	if self.discount:
		for row in self.items:
			row.discount_percentage = self.discount
	
def on_submit(self, method):
	validate_rate(self)