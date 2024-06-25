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
import datetime
from datetime import date
from odoo import http
from odoo.http import request

selection_field = {'resident': 'Residential',
                   'special': 'Specialist'}


class ServiceRequest(http.Controller):
    @http.route(['/doctor_appointment'], type='http', auth="public",
                website=True)
    def doctor_appointment(self):
        """Doctor Appointment form"""
        speciality = request.env['hospital.specialization'].sudo().search([])
        values = {
            'speciality': speciality,

        }
        return request.render("hospital_appointments.doctor_appointment_form",
                              values)

    @http.route('/doctor/slot/booking', methods=['POST', 'GET'], type='http',
                auth="public", website=True, csrf=False)
    def submit_form(self, **kw):
        """Taking appointment to doctor"""
        if kw:
            currency = request.env.user.company_id.currency_id.symbol
            speciality = request.env['hospital.specialization'].browse(
                int(kw.get('spcl_id')))
            doctors = request.env['hr.employee'].browse(int(kw.get('doc_id')))
            consultancy_type = selection_field[doctors.consultancy_type]
            data = {
                'doc_name': doctors,
                'currency': currency,
                'consult_charge': doctors.consultancy_charge,
                'consult_type': consultancy_type,
                'specialization': doctors.specialization,
                'special_id': speciality,
            }
            if not doctors.image_128:
                return request.render(
                    'hospital_appointments.doctor_slot', data)
            else:
                data['image'] = doctors.image_256
            return request.render(
                'hospital_appointments.doctor_slot', data)
        else:
            return request.redirect('/')

    @http.route(['/specialization'], type='json', auth="user", website=True)
    def input_data_processing(self, **kw):
        if kw:
            input_data = kw.get('spcl_id')
            doctors_data = []
            if not input_data == 'Select':
                speciality = request.env['hospital.specialization'].browse(
                    int(input_data))
                doctors = request.env['hr.employee'].search([
                    ('is_doctor', '=', 'doctor'),
                    ('specialization', '=', speciality.id)])
                for rec in doctors:
                    doctors_data.append((rec.id, rec.name))
            data = {
                'doctors': doctors_data,
            }
            return data

    @http.route(['/find/slot'], type='json', auth="user", website=True)
    def input_slot(self, **kw):
        """Booking slot"""
        input_data = kw.get('date')
        date_day = datetime.datetime.strptime(input_data, '%Y-%m-%d').weekday()
        doctors = request.env['hr.employee'].browse(int(kw.get('doc_id')))
        slots = request.env['resource.calendar.attendance'].search([
            ('calendar_id', '=', doctors.resource_calendar_id.id),
            ('dayofweek', '=', date_day)])
        slots_list = []
        for slot in slots:
            if slot.day_period == 'morning' and slot.hour_to == 12:
                period_start = 'am'
                period_end = 'pm'
            elif slot.day_period == 'morning' and slot.hour_to != 12:
                period_start = 'am'
                period_end = 'am'
            else:
                period_start = 'pm'
                period_end = 'pm'
            slots_list.append({
                'slot_id': slot.id,
                'hour_from': slot.hour_from,
                'hour_to': slot.hour_to,
                'period_start': period_start,
                'period_end': period_end
            })
        return slots_list

    @http.route('/create/slot/appointment', methods=['POST', 'GET'],
                type='http',
                auth="public", website=True, csrf=False)
    def submit_slots(self, **kw):
        """Create the appointment"""
        if kw:
            speciality_id = int(kw.get('special_id'))
            doctor_id = int(kw.get('doctor_inv_id'))
            slot_id = int(kw.get('slot_id'))
            appointment_date = kw.get('appointment_date')
            doctors = request.env['hr.employee'].browse(doctor_id)
            slots = request.env['resource.calendar.attendance'].browse(slot_id)
            speciality = request.env['hospital.specialization'].browse(
                speciality_id)
            data = {
                'appointment_date': appointment_date,
                'doctors': doctors,
                'slots': slots,
                'speciality': speciality
            }
            return request.render(
                'hospital_appointments.patient_form', data)
        else:
            return request.redirect('/')

    @http.route('/create/appointment/data', methods=['POST', 'GET'],
                type='http',
                auth="public", website=True, csrf=False)
    def submit_final(self, **kw):
        """Patient details"""
        print(kw, "final kw")
        if kw:
            patient = request.env['res.partner'].sudo().create({
                'name': kw.get('patient_name')})
            age = kw.get("age")
            phone = kw.get('phone')
            email = kw.get('email')
            appointment_date = kw.get('appoint_date')
            gender = kw.get('gender')
            place = kw.get('place')
            registration_date = date.today()
            doctors = request.env['hr.employee'].browse(
                int(kw.get('doctor_name')))
            speciality = request.env['hospital.specialization'].browse(
                int(kw.get('special_id_ne')))
            slot = request.env['resource.calendar.attendance'].browse(
                int(kw.get('slot_id_ne')))
            if slot.day_period == 'morning' and slot.hour_to == 12:
                period_start = 'am'
                period_end = 'pm'
            elif slot.day_period == 'morning' and slot.hour_to != 12:
                period_start = 'am'
                period_end = 'am'
            else:
                period_start = 'pm'
                period_end = 'pm'
            slot = str(int(slot.hour_from)) + ' ' + period_start + ' : ' + str(
                int(slot.hour_to)) + ' ' + period_end
            vals = {
                'patient_id': patient.id,
                "patient_name": patient.id, 'age': age, 'phone': phone,
                'email': email, 'appointment_date': appointment_date,
                'gender': gender,
                'doc_id': doctors.id,
                'speciality': speciality.id,
                'slot': slot,
                'address': place
            }
            appointment = request.env['hospital.appointment'].sudo().create(
                vals)
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
