cur_frm.fields_dict.expense_head.get_query = function(doc) {
	return {
		filters: {
			"company": doc.company
		}
	}
};