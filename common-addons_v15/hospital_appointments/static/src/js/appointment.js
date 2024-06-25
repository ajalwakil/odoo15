odoo.define('hospital_appointments.appointment', function (require) {
    "use strict";
var session = require('web.session');
var rpc = require('web.rpc');
var ajax = require('web.ajax');
var core = require('web.core');
var QWeb = core.qweb;
$(document).ready(function() {
         $("#spcl_id").on("change", function (e) {
            var speciality = document.getElementById("spcl_id").value;
            ajax.jsonRpc("/specialization", 'call', {
                           'spcl_id' : speciality,
                     })
            .then(function (data) {
                $('#doc_id').empty();
                for (let i of data.doctors){
                $('#doc_id').html($('#doc_id').html() + `<option value=${i[0]}>${i[1]}`)
                }
                });
            });

         $('#appointment_date').on("change", function (e) {
             var date = document.getElementById("appointment_date").value;
             var doc = document.getElementById("doctor_inv_id").value;
             document.getElementById('slot_section').style.display = "block"
              ajax.jsonRpc("/find/slot", 'call', {
                           'doc_id': doc,
                           'date' : date,
                     }).then(function (data) {
                       console.log("data", data)

                      $(data).each(function(slot){
                            $('#div_slots').append("<input type='radio' id='slot' name='slot_id' required='1' value="+ data[slot].slot_id +">"+" "+"<span for='slot'>"+ data[slot].hour_from+" "+ data[slot].period_start+" : "+ data[slot].hour_to+" "+ data[slot].period_end+" "+"</span><br/>");
                      })
                      });
         });
});
});