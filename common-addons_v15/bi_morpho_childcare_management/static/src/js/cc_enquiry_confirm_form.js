odoo.define("bi_morpho_childcare_management.cc_enquiry_confirm", function (require) {
 "use strict";

 	var ajax = require("web.ajax");
 	var add_from = require("bi_morpho_childcare_management.addmission_form");

	$(document).ready(function() {

		$("#cc_form_enq_submit").click(function (e){
			if (validateForm("enquiry_form")){
					document.getElementById("enquiry_form").submit();
				}
		});


		function validateForm(id) {
			var x, y, i, valid = true;
			x = document.getElementById(id);
			y = x.getElementsByClassName("form_name");
			for (i = 0; i < y.length; i++) {
				if (y[i].value.length === 0) {
					$(y[i]).addClass("border-danger");
					y[i].style.backgroundColor = "#ffdddd";
					valid = false;
				}
				else{
					y[i].style.backgroundColor = "#ffffff";
				}
			}
			return valid;
		};
	});

});