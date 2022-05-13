import frappe

def before_save(self, method):
    set_income_account(self)

def set_income_account(self):
    if self.income_account:
        for row in self.items:
            row.income_account = self.income_account