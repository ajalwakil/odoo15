odoo.define("bi_morpho_childcare_management.cc_website_template", function (require) {
 "use strict";

 	var ajax = require("web.ajax");

	$(document).ready(function() {

		$("#small_sidebar_btn").click(function(){
			$(".sidebar").css("display","block");
		});

		$("#close_sidebar_btn").click(function(){
			$(".sidebar").css("display","none");
		});

		window.addEventListener("resize", function(){
			if(window.innerWidth > "820") $(".sidebar").css("display","block");
			if(window.innerWidth < "820") $(".sidebar").css("display","none");
		});


		$(".open_chk").click(function(){
			if ($("#child_name").val() === "")
			{
				alert("Enter child to check In / Out");
			}
			else{
				$(".pinpass").val("");
				$(".pinpass_war").css("display","none");
				$(".pinpass_warid").css("display","none");
				$("#checkio_modal").modal("show"); 
			}
		});


		$("#child_name").change(function(){
			if ($("#child_name").val() !== ""){
				ajax.jsonRpc("/cc/chk/name", "call", {
					child_id : $("#child_name").val(),
				}).then(function(data){
					if (data){
						var inout = document.getElementsByClassName("in_out");
						for (var i=0; i<inout.length; i++){
							inout[i].innerHTML = data;
						}
					}
				});
			}
		});


		$(".pinpass").keyup(function(){
			const re =  /^[0-9]+$/;
			if ($(".pinpass")){
				if (! re.test(String($(".pinpass").val()))){
					var ps = $(".pinpass").val();
					ps = ps.slice(0,ps.length-1);
					$(".pinpass").val(ps);
					$(".pinpass_warid").css("display","block");
				}
				else{
					$(".pinpass_warid").css("display","none");
				}
			}
		});


		$(".pinpass").click(function(){
			$(".pinpass_war").css("display","none");
		});


		$(".chk_btn").click(function(){
			const re =  /^[0-9]+$/;
			if ($(".pinpass")){
				const pin = $(".pinpass").val();
				if (pin === "" || pin.length !== 4){
					$(".pinpass_war").css("display","block");
				}
				else if (! re.test(String(pin))){
					$(".pinpass_war").css("display","block");
				}
				else {
					var inout = document.getElementsByClassName("in_out")[0].innerHTML;
					ajax.jsonRpc("/my/cc/childs/checkinout", "call", {
						"child_id" : $("#child_name").val(),
						"inout" : inout,
						"pinpass" : $(".pinpass").val(),
					}).then(function(data){
						if (data.warning){
							alert(data.warning);
						}
						if (data.success){
							$("#checkio_modal").modal("hide");
							window.location.reload();
							alert(data.message);
						}
					});
				}
			}
			
		});


		$("#child_name2").click(function(){
			$(".pe_child_war").css("display","none");
			if($("#child_name2").val() === ""){
				$("#main_session_content").css("display","none");
				$("#main_feed_content").css("display","none");
			}
		});


		$(".feed_button_feed").click(function(){
			if($("#child_name2").val() === ""){
				$(".pe_child_war").css("display","block")
			}
			else{
				var child = $("#child_name2").val();
				$("#main_session_content").css("display","none");
				$(".child_sess").css("display","none");
				$(".child_feed").css("display","none");
				$("#main_feed_content").css("display","block");
				$(".child_feed_" + child).css("display","block");
			}
		});


		$(".feed_button_session").click(function(){
			if($("#child_name2").val() === ""){
				$(".pe_child_war").css("display","block")
			}
			else{
				var child = $("#child_name2").val();
				$("#main_feed_content").css("display","none");
				$(".child_feed").css("display","none");
				$(".child_sess").css("display","none");
				$("#main_session_content").css("display","block");
				$(".child_sess_" + child).css("display","block");
			}
			
		});



		$("#child_act_re").click(function(){
			if($("#child_name3").val() === ""){
				$(".re_child_war").css("display","block");
			}else{
				$(".re_child_war").css("display","none");
			}
		});


		$("#child_nutr_re").click(function(){
			if($("#child_name3").val() === ""){
				$(".re_child_war").css("display","block");
			}else{
				$(".re_child_war").css("display","none");
			}
		});


		$("#child_name3").click(function(){
			if($("#child_name3").val() === ""){
				$("#child_act_re").attr("href","#")
				$("#child_nutr_re").attr("href","#")
				$(".re_child_war").css("display","block")
			}
			else{
				$(".re_child_war").css("display","none");
				var child = $("#child_name3").val();
				var tokan = $("#csrf_token").val();
				$("#child_act_re").attr("href",`/my/cc/child/reports?access_token=${tokan}&child_id=${child}&report_no=1&report_type=pdf&download=true`)
				$("#child_nutr_re").attr("href",`/my/cc/child/reports?access_token=${tokan}&child_id=${child}&report_no=3&report_type=pdf&download=true`)
			}
		});


		$("#child_att_re").click(function(){
			if($("#child_name3").val() === ""){
				$(".re_child_war").css("display","block");
			}else{
				$(".re_child_war").css("display","none");
				$("#cc_re_btns").css("display","none");
				$(".re_att_body").css("display","block");
			}
		});


		$(".re_att_cancel").click(function(){
			$(".re_child_war").css("display","none");
			$("#cc_re_btns").css("display","block");
			$(".re_att_body").css("display","none");
		})



		$("#stdate").change(function(){
			$("#att_dates_war").css("display","none");
			if($("#stdate").val() === "" || $("#endate").val() === "" ){
				$("#child_att_rep").attr("href","#");
			}else{
				var stdate = $("#stdate").val();
				var endate = $("#endate").val();
				var child = $("#child_name3").val();
				var tokan = $("#csrf_token").val();
				$("#child_att_rep").attr("href",`/my/cc/child/reports?access_token=${tokan}&child_id=${child}&report_no=2&sdate=${stdate}&edate=${endate}&report_type=pdf&download=true`);
			}
		});

		$("#endate").change(function(){
			$("#att_dates_war").css("display","none");
			if($("#stdate").val() === "" || $("#endate").val() === "" ){
				$("#child_att_rep").attr("href","#");
			}else{
				var stdate = $("#stdate").val();
				var endate = $("#endate").val();
				var child = $("#child_name3").val();
				var tokan = $("#csrf_token").val();
				$("#child_att_rep").attr("href",`/my/cc/child/reports?access_token=${tokan}&child_id=${child}&report_no=2&sdate=${stdate}&edate=${endate}&report_type=pdf&download=true`);
			}
		});



		$("#child_att_rep").click(function(){
			if($("#stdate").val() === "" || $("#endate").val() === "" ){
				$("#att_dates_war").css("display","block");
			}else{
				$("#att_dates_war").css("display","none");
				$("#cc_re_btns").css("display","block");
				$(".re_att_body").css("display","none");
			}
		})

	});


	


	var core = require('web.core');
	const dom = require('web.dom');
	var publicWidget = require('web.public.widget');
	var time = require('web.time');
	var portalComposer = require('portal.composer');

	var qweb = core.qweb;
	var _t = core._t;
	var portalChatter = require('portal.chatter');

	portalChatter.PortalChatter.prototype.xmlDependencies = [
		'/portal/static/src/xml/portal_chatter.xml',
		'/bi_morpho_childcare_management/static/src/xml/cc_portal_chatter.xml'
	];


	portalChatter.PortalChatter.include({

		init: function (parent, options) {
			this._super.apply(this, arguments);
			if (this.options.is_cc === 1){
				this.set("cc_chatter",true);
			}else{
				this.set("cc_chatter",false);
			}
		},


		_messageFetchPrepareParams: function () {
			var data = this._super.apply(this);
	        var self = this;
	        if (this.get("cc_chatter")){
	        	data.domain = data.domain.concat([["cc_attachment","=",true]]) 
	        	data.is_parent = true;
	        }
	       	return data;
	    },


	    getMimeType: function (mimeType) {
            switch (mimeType) {
                case 'application/pdf':
                    return 'application/pdf';
                case 'image/bmp':
                case 'image/gif':
                case 'image/jpeg':
                case 'image/png':
                case 'image/svg+xml':
                case 'image/tiff':
                case 'image/x-icon':
                    return 'image';
                case 'application/javascript':
                case 'application/json':
                case 'text/css':
                case 'text/html':
                case 'text/plain':
                    return 'text';
                case 'audio/mpeg':
                case 'video/x-matroska':
                case 'video/mp4':
                case 'video/webm':
                    return 'video';
                case 'application/octet-stream':
                	return 'application/octet-stream';
            }
	    	return false;
	    },

	    _computeDefaultSource : function(attachment) {
	    	var fileType = this.getMimeType(attachment.mimetype)
            if (fileType === 'image') {
                return `/web/image/${attachment.id}?unique=1&amp;signature=${attachment.checksum}&amp;model=ir.attachment`;
            }
            if (fileType === 'application/pdf') {
                return `/web/static/lib/pdfjs/web/viewer.html?file=/web/content/${attachment.id}?model%3Dir.attachment`;
            }
            if (fileType && fileType.includes('text')) {
                return `/web/content/${attachment.id}?model%3Dir.attachment`;
            }
            if (fileType === 'video') {
                return `/web/content/${attachment.id}?model=ir.attachment`;
            }
            return false;
        }
	})


});