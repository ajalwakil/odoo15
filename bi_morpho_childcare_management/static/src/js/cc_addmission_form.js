odoo.define("bi_morpho_childcare_management.addmission_form", function (require) {
 "use strict";

 	var ajax = require("web.ajax");

	$(document).ready(function() {

		$('#parent_add_country').change(function (){
			var country_id = $('#parent_add_country').val();
			if (country_id){
			    if ($("option[data-country=" + country_id +"]").length){
			        $("option[data-country=" + country_id +"]").css('display','block');
			    }
			    else{
			        $('.state_options').css('display','none');
			    }
			}
			else{
			    $('.state_options').css('display','none');
			}
		});

		

		$("#add_allergy").click(function(e){
			if(validateForm("alg_modal_body_div")){
				var name = document.getElementsByName("alg_name")[0].value;
				var des = document.getElementsByName("alg_des")[0].value;
				var trs = $(".alg_table").find("tbody>tr");
				var count = trs.length + 1;
				ajax.jsonRpc("/cc/add/allergy", "call", {
					"name": name,
					"des": des,
				}).then(function(data){
					$(".alg_mdl_dis").click();
					var classname = name + count;
					var TrElement = '<tr data-model="alg" data-recid="'+count+'" class="'+classname+'"><td>'+name+'</td><td>'+des+'</td><td><a href="#" style="text-decoration:none;" data-recid="'+count+'" role="button" class="alg_del" data-classname="'+ classname+'">x</a></td></tr>';
					$(".alg_table").find('tbody').append(TrElement);
					document.getElementsByName("alg_name")[0].value = "";
					document.getElementsByName("alg_des")[0].value = "";
				});
			}
		});

		$("#edit_allergy").click(function(e){
			if(validateForm("alg_modal_body_div")){
				var name = document.getElementsByName("alg_name")[0].value;
				var des = document.getElementsByName("alg_des")[0].value;
				var id = e.currentTarget.dataset.recid;
				ajax.jsonRpc("/cc/edit/allergy", "call", {
					"name": name,
					"des": des,
					"id": id,
				}).then(function(data){
					if (data){
						$(".alg_mdl_dis").click();
						document.getElementsByName("medi_name")[0].value = "";
						document.getElementsByName("medi_des")[0].value = "";
						$('#add_allergy').css('display', 'block');
						$('#edit_allergy').css('display', 'none');
						if ($("#alg_table_body").find("tr[data-recid='"+id+"']")[0] && $("#alg_table_body").find("tr[data-recid='"+id+"']")[0].childNodes){
							$("#alg_table_body").find("tr[data-recid='"+id+"']")[0].childNodes[0].innerHTML = name;
							$("#alg_table_body").find("tr[data-recid='"+id+"']")[0].childNodes[1].innerHTML = des;
						}
					}
					else{
						$(".alg_mdl_dis").click();
						document.getElementsByName("alg_name")[0].value = "";
						document.getElementsByName("alg_des")[0].value = "";
						$('#add_allergy').css('display', 'block');
						$('#edit_allergy').css('display', 'none');
						alert("Unable to update record.");
					}
				});
			}
		});

		$("#alg_table_body").click(function(e){
			if (e.target.className == "alg_del" && e.target.dataset.classname){
				ajax.jsonRpc("/cc/del/allergy", "call", {
					"no" : e.target.dataset.recid,
				}).then(function(data){
					if (data == true){
						var deletedTR = document.getElementsByClassName(e.target.dataset.classname);
					  	document.getElementById("alg_table_body").removeChild(deletedTR[0]);
					}
					else{
						alert("Not able to remove the allergy.");
					}
				});
			}
			if (e.target.nodeName == "TD" && e.target.parentElement){
				if(e.target.parentElement.childNodes[0] && e.target.parentElement.childNodes[1]){
					document.getElementsByName("alg_name")[0].value = e.target.parentElement.childNodes[0].innerText;
					document.getElementsByName("alg_des")[0].value = e.target.parentElement.childNodes[1].innerText;
				}
				$('#add_allergy').css('display', 'none');
				$('#edit_allergy').css('display', 'block');
				$('#edit_allergy').attr('data-recid', e.target.parentElement.dataset.recid);
				$('#myModal').modal('show');
			}
		});


		$(".alg_mdl_dis").click(function(){
			document.getElementsByName("alg_name")[0].value = "";
			document.getElementsByName("alg_des")[0].value = "";
		});



		$("#add_medication").click(function(e){
			if(validateForm("medi_modal_body_div")){
				var name = document.getElementsByName("medi_name")[0].value;
				var des = document.getElementsByName("medi_des")[0].value;
				var trs = $(".medi_table").find("tbody>tr");
				var count = trs.length + 1;
				ajax.jsonRpc("/cc/add/medication", "call", {
					"name": name,
					"des": des,
				}).then(function(data){
					$(".medi_mdl_dis").click();
					var classname = name + count;
					var TrElement = '<tr data-model="medi" data-recid="'+count+'" class="'+classname+'"><td>'+name+'</td><td>'+des+'</td><td><a href="#" style="text-decoration:none;" data-recid="'+count+'" role="button" class="medi_del" data-classname="'+ classname+'">x</a></td></tr>';
					$(".medi_table").find('tbody').append(TrElement);
					document.getElementsByName("medi_name")[0].value = "";
					document.getElementsByName("medi_des")[0].value = "";
				});
			}
		});

		$("#edit_medication").click(function(e){
			if(validateForm("medi_modal_body_div")){
				var name = document.getElementsByName("medi_name")[0].value;
				var des = document.getElementsByName("medi_des")[0].value;
				var id = e.currentTarget.dataset.recid;
				ajax.jsonRpc("/cc/edit/medication", "call", {
					"name": name,
					"des": des,
					"id": id,
				}).then(function(data){
					if (data){
						$(".medi_mdl_dis").click();
						document.getElementsByName("medi_name")[0].value = "";
						document.getElementsByName("medi_des")[0].value = "";
						$('#add_medication').css('display', 'block');
						$('#edit_medication').css('display', 'none');
						if ($("#medi_table_body").find("tr[data-recid='"+id+"']")[0] && $("#medi_table_body").find("tr[data-recid='"+id+"']")[0].childNodes){
							$("#medi_table_body").find("tr[data-recid='"+id+"']")[0].childNodes[0].innerHTML = name;
							$("#medi_table_body").find("tr[data-recid='"+id+"']")[0].childNodes[1].innerHTML = des;
						}
					}
					else{
						$(".medi_mdl_dis").click();
						document.getElementsByName("medi_name")[0].value = "";
						document.getElementsByName("medi_des")[0].value = "";
						$('#add_medication').css('display', 'block');
						$('#edit_medication').css('display', 'none');
						alert("Unable to update record.");
					}
				});
			}
		});

		


		$("#medi_table_body").click(function(e){
			if (e.target.className == "medi_del" && e.target.dataset.classname){
				ajax.jsonRpc("/cc/del/medication", "call", {
					"no" : e.target.dataset.recid,
				}).then(function(data){
					if (data == true){
						var deletedTR = document.getElementsByClassName(e.target.dataset.classname);
					  	document.getElementById("medi_table_body").removeChild(deletedTR[0]);
					}
					else{
						alert("Not able to remove the medication.");
					}
				});
			}
			if (e.target.nodeName == "TD" && e.target.parentElement){
				if(e.target.parentElement.childNodes[0] && e.target.parentElement.childNodes[1]){
					document.getElementsByName("medi_name")[0].value = e.target.parentElement.childNodes[0].innerText;
					document.getElementsByName("medi_des")[0].value = e.target.parentElement.childNodes[1].innerText;
				}
				$('#add_medication').css('display', 'none');
				$('#edit_medication').css('display', 'block');
				$('#edit_medication').attr('data-recid', e.target.parentElement.dataset.recid);
				$('#myModalMedi').modal('show');
			}
			
		});


		
		$(".medi_mdl_dis").click(function(){
			document.getElementsByName("medi_name")[0].value = "";
			document.getElementsByName("medi_des")[0].value = "";
		});



		$(".form_name").click(function(){
			$(this).removeClass("border-danger");
			$(this).css("background-color","#ffffff");
		})


		$("#cc_form_submit").click(function (e){
			if (validateForm("add_form") && fields_validation_function('email') && 
				fields_validation_function('phone') && fields_validation_function('mobile')){
				$("#fields_mand").css("display","none");
				document.getElementById("add_form").submit();
			}else{
				$("#fields_mand").css("display","block");
			}
		});
	

		function validateForm(id) {
			var x, y, i, valid = true;
			x = document.getElementById(id);
			y = x.getElementsByClassName("form_name");
			for (i = 0; i < y.length; i++) {
				if (y[i].value.length === 0) {
					$(y[i]).addClass("border-danger");
					y[i].style.backgroundColor = "#ffdbdb";
					valid = false;
				}
				else{
					y[i].style.backgroundColor = "#ffffff";
				}
			}
			return valid;
		};


		function fields_validation_function(field){
			if (field === 'email'){
				const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
	    		if (! re.test(String($('.valid_email').val()))){
		    		$('.valid_email').addClass('border-danger');
		    		$('.valid_email_war').show();
		    		return false;
		    	}
		    	else{
		    		$('.valid_email').removeClass('border-danger');
		    		$('.valid_email_war').hide();
		    		return true;
		    	}
			}

			if (field === 'phone'){
				const re =  /^[0-9]+$/;
				if ($('.valid_phone').val().length > 12){
					$('.valid_phone').addClass('border-danger');
		    		$('.valid_phone_war').show();
		    		return false;
				}
				if (! re.test(String($('.valid_phone').val()))){
		    		$('.valid_phone').addClass('border-danger');
		    		$('.valid_phone_war').show();
		    		return false;
		    	}
		    	else{
		    		$('.valid_phone').removeClass('border-danger');
		    		$('.valid_phone_war').hide();
		    		return true;
		    	}

		    }

		    if (field === 'mobile'){
				const re =  /^[0-9]+$/;
				if ($('.valid_mobile').val().length > 12){
					$('.valid_mobile').addClass('border-danger');
		    		$('.valid_mobile_war').show();
		    		return false;
				}
				if (! re.test(String($('.valid_mobile').val()))){
		    		$('.valid_mobile').addClass('border-danger');
		    		$('.valid_mobile_war').show();
		    		return false;
		    	}
		    	else{
		    		$('.valid_mobile').removeClass('border-danger');
		    		$('.valid_mobile_war').hide();
		    		return true;
		    	}

		    }
		};

	});
});