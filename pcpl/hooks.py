# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "pcpl"
app_title = "Pcpl"
app_publisher = "STPL"
app_description = "Prince"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "umesh.garala@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------
app_include_js = [
	"pcpl.bundle.js",
	#"assets/finbyzerp/js/frappe/ui/page.js"
]
# include js, css files in header of desk.html
# app_include_css = "/assets/pcpl/css/pcpl.css"
# app_include_js = "/assets/pcpl/js/pcpl.js"

# include js, css files in header of web template
# web_include_css = "/assets/pcpl/css/pcpl.css"
# web_include_js = "/assets/pcpl/js/pcpl.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "pcpl/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Purchase Invoice" : "public/js/purchase_invoice.js",
    "Sales Invoice" : "public/js/sales_invoice.js",
    "Sales Order" : "public/js/sales_order.js",
    "Delivery Note" : "public/js/delivery_note.js",
    "Journal Entry" : "public/js/journal_entry.js",
    "Stock Entry" : "public/js/stock_entry.js"
    
    }
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "pcpl.install.before_install"
# after_install = "pcpl.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "pcpl.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "*": {
	# 	"on_update": "method",
	# 	"on_cancel": "method",
	# 	"on_trash": "method"
	# }
    "Sales Invoice": {
        "before_save": "pcpl.pcpl.doc_events.sales_invoice.before_save",
        "before_submit": "pcpl.pcpl.doc_events.sales_invoice.before_submit",
        "validate": "pcpl.pcpl.doc_events.sales_invoice.validate"
    },
    "Purchase Invoice": {
        "before_save": "pcpl.pcpl.doc_events.purchase_invoice.before_save"
    },
    "Sales Secondary":{
        "before_naming": "finbyzerp.api.before_naming",
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"pcpl.tasks.all"
# 	],
# 	"daily": [
# 		"pcpl.tasks.daily"
# 	],
# 	"hourly": [
# 		"pcpl.tasks.hourly"
# 	],
# 	"weekly": [
# 		"pcpl.tasks.weekly"
# 	]
# 	"monthly": [
# 		"pcpl.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "pcpl.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "pcpl.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "pcpl.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


from pcpl.pcpl.report.trial_balance_for_party import execute as trial_balance_for_party_execute
from erpnext.accounts.report.trial_balance_for_party import trial_balance_for_party
trial_balance_for_party.execute = trial_balance_for_party_execute

# from pcpl.pcpl.doc_events import sales_invoice
# from finbyzerp.e_invoice_override import validate_einvoice_fields as vef
# sales_invoice.validate_einvoice_fields = vef

from pcpl.api import get_delivery_notes_to_be_billed as api_get_delivery_notes_to_be_billed
from erpnext.controllers import queries
queries.get_delivery_notes_to_be_billed = api_get_delivery_notes_to_be_billed