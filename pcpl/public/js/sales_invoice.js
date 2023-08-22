cur_frm.fields_dict.income_account.get_query = function(doc) {
	if(doc.company == "Prince Care Pharma Pvt. Ltd."){
		return {
			filters:{
				'account_type':"Income Account",
				'company': doc.company
			}
		}
	} else if(doc.company == "Prince Supplico"){
        return {
            filters: {
                'account_type':"Income Account",
                "company": doc.company
            }
        }
    }
};
cur_frm.fields_dict.contact_person_2.get_query = function(doc) {
	return {
		filters: {
			"link_doctype":"Customer",
			"link_name":doc.customer
		}
	}
};
cur_frm.fields_dict.tds_account.get_query = function(doc) {
	return {
		filters: {
			"is_tds_account": 1
		}
	}
};

frappe.ui.form.on("Sales Invoice", {
    customer: function(frm){
		if (frm.doc.customer){
			frappe.model.get_value("Customer",frm.doc.customer,"income_account",(r)=>{
				if(r.income_account){
					frm.set_value('income_account',r.income_account)
				}
			})
		}else{
			frm.set_value('income_account', "")
		}
	},
	calculate_tds_taxes:function (frm)
    {
        if(frm.doc.tds_account){
            frm.trigger('taxes_set_values')
        }
        else{
            frappe.throw(__('First Select TDS Account'))
        }

    },
    before_save: function(frm,cdt,cdn) {
        var doc = locals[cdt][cdn];
        if(!frm.doc.date_removal){
          frappe.model.set_value(cdt, cdn, 'date_removal', doc.posting_date);
        }
        frm.doc.items.forEach((row)=>{
            frm.call({
                method: 'pcpl.pcpl.doctype.sales_secondary.sales_secondary.get_price_list_rate_for',
                "args": {
                    "item_code": row.item_code,
                    "price_list": frm.doc.selling_price_list,
                    "uom": row.uom,
                    "posting_date":frm.doc.posting_date
                },
                callback: function(res){
                    frappe.model.set_value(cdt, cdn, 'free_item_pricelist_rate', res.message);
                }
            });
        });
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
 
    taxes_set_values:function(frm){
        
        let total_rate = 0.0;
        frm.doc.items.forEach(function (i) {
            total_rate += flt((i.qty*i.free_item_pricelist_rate));
        });
        frm.set_value("total_mrp_amount",total_rate)
        var tds_account_head = [];
        
        frm.doc.taxes.forEach(function(i) {
            tds_account_head.push(i.account_head);
        }); 

        if(!tds_account_head.includes(frm.doc.tds_account)){
            var childTable = cur_frm.add_child("taxes");
            childTable.account_head = frm.doc.tds_account
            childTable.rate = 0.0
            childTable.charge_type = "Actual"
            childTable.tax_amount = (total_rate/10)
            cur_frm.refresh_fields("taxes");
        }
        
    },
    naming_series: function(frm){
        frm.set_query("customer", function() {
			return {
				filters : {
                    "is_secondary_customer": 0
                }
            }
        })
        if(frm.doc.naming_series=="SIA-2223-.####")
            frm.set_value("income_account","Sales Allopathic - PC")
    }
})

frappe.ui.form.on('Sales Invoice Item',{
	item_code: function (frm,cdt,cdn){
        var row = locals[cdt][cdn]
        if(frm.doc.taxes){
            frm.doc.taxes.forEach(function(i) {
                let id = i.idx - 1;
                if (i.account_head == frm.doc.tds_account) {
                    frm.get_field("taxes").grid.grid_rows[id].remove();
                }
            })
        }
        if(row.item_code && frm.doc.selling_price_list && frm.doc.posting_date){
            frappe.model.get_value("Item",row.item_code,'stock_uom',(r)=>{
                if(r.stock_uom){
                    frm.call({
                        method: 'pcpl.pcpl.doctype.sales_secondary.sales_secondary.get_price_list_rate_for',
                        "args": {
                            "item_code": row.item_code,
                            "price_list": frm.doc.selling_price_list,
                            "uom": r.stock_uom,
                            "posting_date":frm.doc.posting_date
                        },
                        callback: function(res){
                            frappe.model.set_value(cdt, cdn, 'free_item_pricelist_rate', res.message);
                        }
                    });
                }

            })
			
		}
    },
    free_item: function(frm,cdt,cdn) {
        var doc = locals[cdt][cdn];
       if(doc.free_item == 1){
          frappe.model.set_value(cdt, cdn, 'price_list_rate', 0);
       }
    }
})

