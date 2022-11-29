cur_frm.fields_dict.expense_head.get_query = function(doc) {
	if(doc.company == "Prince Care Pharma Pvt. Ltd."){
        return {
            filters: {
                'account_type':"Expense Account",
                "company": doc.company
            }
        }
    }else if(doc.company == "Prince Supplico"){
        return {
            filters: {
                'account_type':"Expense Account",
                "company": doc.company
            }
        }
    }
	
};