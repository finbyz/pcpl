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
	before_save: function(frm){
		frm.doc.items.forEach((item) => {
            frappe.model.set_value(item.doctype, item.name, "discount_percentage", frm.doc.discount);
			let effective_item_rate = item.price_list_rate;
			let item_rate = item.rate;
			if (in_list(["Sales Order", "Quotation"], item.parenttype) && item.blanket_order_rate) {
				effective_item_rate = item.blanket_order_rate;
			}
			if (item.margin_type == "Percentage") {
				item.rate_with_margin = flt(effective_item_rate)
					+ flt(effective_item_rate) * ( flt(item.margin_rate_or_amount) / 100);
			} else {
				item.rate_with_margin = flt(effective_item_rate) + flt(item.margin_rate_or_amount);
			}
			item.base_rate_with_margin = flt(item.rate_with_margin) * flt(frm.doc.conversion_rate);

			item_rate = flt(item.rate_with_margin , precision("rate", item));

			if (item.discount_percentage) {
				item.discount_amount = flt(item.rate_with_margin) * flt(item.discount_percentage) / 100;
			}

			if (item.discount_amount) {
				item_rate = flt((item.rate_with_margin) - (item.discount_amount), precision('rate', item));
				item.discount_percentage = 100 * flt(item.discount_amount) / flt(item.rate_with_margin);
			}

			frappe.model.set_value(item.doctype, item.name, "rate", item_rate);
        });
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
