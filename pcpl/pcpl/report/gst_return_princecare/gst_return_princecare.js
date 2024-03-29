// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

{% include "erpnext/accounts/report/item_wise_sales_register/item_wise_sales_register.js" %}
{% include "india_compliance/gst_india/report/utils.js" %}

let filters = frappe.query_reports["Item-wise Sales Register"]["filters"];

// Add GSTIN filter
filters = filters.concat({
    "fieldname":"company_gstin",
    "label": __("Company GSTIN"),
    "fieldtype": "Select",
    "placeholder":"Company GSTIN",
    "options": [""],
    "width": "80"
}, {
    "fieldname":"invoice_type",
    "label": __("Invoice Type"),
    "fieldtype": "Select",
    "placeholder":"Invoice Type",
    "options": ["", "Regular", "SEZ", "Export", "Deemed Export"]
},{
    "fieldname":"gst_category",
    "label": __("GST Category"),
    "fieldtype": "Select",
    "placeholder":"GST Category",
    "options": ["", "Registered Regular", "Registered Composition", "Unregistered", "SEZ", "Overseas", "Consumer", "Deemed Export", "UIN Holders"]
}
);

// Handle company on change
for (var i = 0; i < filters.length; ++i) {
    if (filters[i].fieldname === 'company') {
        filters[i].on_change = fetch_gstins;
    }
}

frappe.query_reports["GST Return Princecare"] = { "filters": filters, "onload": fetch_gstins };