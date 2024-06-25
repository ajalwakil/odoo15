# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from datetime import date
from odoo import http
from odoo.http import request


class ServiceRequest(http.Controller):
    @http.route(['/appointment'], type='http', auth="public", website=True)
    def service_request(self):
        """Appointment form"""
        doctor = request.env['hr.employee'].sudo().search([
            ('is_doctor', '=', 'doctor')])
        values = {
            'doc_name': doctor
        }
        return request.render("hospital_appointments.appointment_form", values)

    @http.route('/create/appointment', methods=['POST', 'GET'], type='http',
                auth="public", website=True, csrf=False)
    def submit_form(self, **kw):
        """Taking appoint to doctor"""
        if kw:
            patient = request.env['res.partner'].sudo().create({
                'name': kw.get('patient_name')})
            patient_name = kw.get("patient_name")
            age = kw.get("age")
            phone = kw.get('phone')
            email = kw.get('email')
            appointment_date = kw.get('appointment_date')
            gender = kw.get('gender')
            registration_date = date.today()
            # qr_code = patient._compute_qr_code()
            vals = {
                'patient_id': patient.id,
                "patient_name": patient.id, 'age': age, 'phone': phone,
                'email': email, 'appointment_date': appointment_date,
                'gender': gender,
                # 'qr_code': qr_code,
            }
            appointment = request.env['hospital.appointment'].sudo().create(vals)
            qr_code = appointment._compute_qr_code()
            vals['qr_code'] = qr_code
            vals['registration_date'] = registration_date
            return request.render(
                'hospital_appointments.appointment_thanks', vals)
        else:
            return request.redirect('/')

    @http.route('/print/appointment', methods=['POST', 'GET'], type='http',
                auth="public", website=True, csrf=False)
    def print_report(self, **kwargs):
        """Printing the patient card after taking appointments"""
        user_obj = request.env.user
        patient_id = kwargs['patient_id']
        appointment_seq = kwargs["appointment_seq"]
        patient_object = request.env['hospital.appointment'].sudo().search([
            ("appointment_seq", "=", appointment_seq)])
        if patient_id:
            pdf, _ = request.env.ref(
                'hospital_appointments.print_patient_card').sudo()._render_qweb_pdf(
                [patient_object.id])
            pdfhttpheaders = [('Content-Type', 'application/pdf'),
                              ('Content-Length', len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)
