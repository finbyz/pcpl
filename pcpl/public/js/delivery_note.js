frappe.ui.form.on("Delivery Note", {
    naming_series: function(frm){
        frm.set_query("customer", function() {
			return {
				filters : {
                    "is_secondary_customer": 0
                }
            }
        })
    },
	contact_person: function(frm){
		if(frm.doc.contact_person){
		}
		else{
			frm.doc.contact_display = " "
		}
	},
	refresh: function(frm){
		if(frm.doc.docstatus==1 && !frm.doc.is_return && frm.doc.status == "Completed") {
			// show Make Invoice button only if Delivery Note is not created from Sales Invoice
			var from_sales_invoice = false;
			from_sales_invoice = frm.doc.items.some(function(item) {
				return item.against_sales_invoice ? true : false;
			});

			frm.add_custom_button(__('Sales Invoice For Free Item'), function() { 
				frappe.model.open_mapped_doc({
					method: "erpnext.stock.doctype.delivery_note.delivery_note.make_sales_invoice",
					frm: frm
				})
			 },
				__('Create'));
		}
	}
})
cur_frm.fields_dict.contact_person_2.get_query = function(doc) {
	return {
		filters: {
			"link_doctype":"Customer",
			"link_name":doc.customer
		}
	}
};