cur_frm.fields_dict.bom_no.get_query = function(doc) {
	return {
	
			filters:{
					"docstatus": 1,
					"is_active": 1,
					"is_default":1
				}
		
	}
};