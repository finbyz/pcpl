import frappe
from pcpl.pcpl.doc_events.sales_invoice import validate_rate

def before_validate(self, method):
	if self.discount:
		for row in self.items:
			row.discount_percentage = self.discount
	
def on_submit(self, method):
	validate_rate(self)