import frappe

def validate(self,method):
	validate_s_and_t_warehoouse(self)
	
def validate_s_and_t_warehoouse(self):
	if self.purpose in ["Material Transfer","Material Transfer for Manufacture"]:
		for row in self.items:
			if row.s_warehouse == row.t_warehouse:
				frappe.throw("Source and Target warehouse can not be same for materil transfer entry.")