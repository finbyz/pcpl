import frappe
def before_validate(self, method):
    if self.discount:
        for row in self.items:
            row.discount_percentage = self.discount