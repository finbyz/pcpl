import frappe

def before_save(self, method):
    set_expence_account(self)

def set_expence_account(self):
    if self.expense_head:
        for row in self.items:
            row.expense_account = self.expense_head