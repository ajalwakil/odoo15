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
{
    'name': "Patient Appointment Management",
    'summary': """Patient Appointment Management. The module will helps to 
    create an doctor appointment through the website""",
    'description': """This module will helps to create the doctor appointment 
    through the website. The patient can choose the doctor and doctor's slot 
    from the website form itself. And patient can fill their details for the 
    appointment. After the submission of appointment, the patient get the 
    patient card.""",
    'author': "Cybrosys Techno Solutions",
    'company': "Cybrosys Techno Solutions",
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    "license": "AGPL-3",
    'category': 'Website',
    'version': '15.0.1.0.1',
    'depends': ['website_sale', 'base_hospital_management'],
    'data': ['security/ir.model.access.csv',
             'reports/patient_card.xml',
             'reports/card_template.xml',
             'reports/patient_card_back.xml',
             'data/appointment_seq.xml',
             'data/mail_template.xml',
             'data/appointment_cancel_template.xml',
             'data/doctor_seq.xml',
             'views/doctor_appointment_views.xml',
             'views/doctor_slot_views.xml',
             'views/hospital_appointments_views.xml',
             'views/hr_employee_views.xml',
             'views/patient_form_views.xml',
             'views/snippets_views.xml',
             'views/thanks_views.xml',
             'views/website_menu_views.xml',
             ],
    'assets': {
        'web.assets_frontend': [
            'hospital_appointments/static/src/js/appointment.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}