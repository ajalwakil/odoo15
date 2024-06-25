odoo.define("sh_electronic_pos_qr_saudi.pos", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    var DB = require("point_of_sale.DB");
    const Registries = require("point_of_sale.Registries");
    const ReceiptScreen = require("point_of_sale.ReceiptScreen");
    const { useRef, useContext } = owl.hooks;
    var core = require('web.core');
    var _t = core._t;
    const OrderReceipt = require('point_of_sale.OrderReceipt')
    const TicketScreen = require("point_of_sale.TicketScreen");


    models.load_models({
        model: "sh.pos.config.qr.elements",
        label: "load_qr_elements",
        loaded: function (self, All_qr_elemet) {
            self.db.all_qr_elemets = All_qr_elemet;
            if (All_qr_elemet && All_qr_elemet.length > 0) {
                _.each(All_qr_elemet, function (each_qr_element) {
                    self.db.qr_elemet_by_id[each_qr_element.id] = each_qr_element
                });
            }
        },
    })
    models.load_fields('res.company', ['sh_arabic_name', 'street', 'city', 'zip', 'arabic_street', 'arabic_street2', 'arabic_city', 'arabic_zip'])
    models.load_fields('res.partner', ['sh_cr_no'])
    models.load_fields('product.product', ['sh_arabic_name'])
    models.load_fields('pos.payment.method', ['sh_payment_method_arabic_name'])

    DB.include({
        init: function (options) {
            this._super.apply(this, arguments);
            this.qr_elemet_by_id = {};
        },
    });

    var _super_Orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        export_for_printing: function () {
            var res = _super_Orderline.export_for_printing.apply(this, arguments)
            res['sh_arabic_name'] = this.get_product().sh_arabic_name;
            res['line_note'] = this.note;
            return res
        }
    })

    var _super_Paymentline = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({
        export_for_printing: function () {
            var res = _super_Paymentline.export_for_printing.apply(this, arguments)
            res['sh_payment_method_arabic_name'] = this.payment_method.sh_payment_method_arabic_name
            return res
        }
    });

    const PosResOrderReceipt = (ReceiptScreen) =>
    class extends ReceiptScreen {
        constructor() {
            super(...arguments)
            this.shorderReceipt = useRef('order-receipt');
        }
        compute_sa_qr_code(name, vat, date_isostring, amount_total, amount_tax) {


            /* Generate the qr code for Saudi e-invoicing. Specs are available at the following link at page 23
            https://zatca.gov.sa/ar/E-Invoicing/SystemsDevelopers/Documents/20210528_ZATCA_Electronic_Invoice_Security_Features_Implementation_Standards_vShared.pdf
            */
            const seller_name_enc = this._compute_qr_code_field(1, name);
            const company_vat_enc = this._compute_qr_code_field(2, vat);
            const timestamp_enc = this._compute_qr_code_field(3, date_isostring);
            const invoice_total_enc = this._compute_qr_code_field(4, Math.round(amount_total,2).toString().replace('-',''));
            const total_vat_enc = this._compute_qr_code_field(5,  Math.round(amount_tax,2).toString().replace('-',''));

            const str_to_encode = seller_name_enc.concat(company_vat_enc, timestamp_enc, invoice_total_enc, total_vat_enc);

            let binary = '';
            for (let i = 0; i < str_to_encode.length; i++) {
                binary += String.fromCharCode(str_to_encode[i]);
            }

            return btoa(binary);
        }

        _compute_qr_code_field(tag, field) {
            const textEncoder = new TextEncoder();
            const name_byte_array = Array.from(textEncoder.encode(field));
            const name_tag_encoding = [tag];
            const name_length_encoding = [name_byte_array.length];
            return name_tag_encoding.concat(name_length_encoding, name_byte_array);
        }
        mounted() {
            var self = this;
            var dic = {}
            var is_gcc_country = ['SA', 'AE', 'BH', 'OM', 'QA', 'KW'].includes(self.env.pos.company.country.code);
            if (self.env.pos.config.display_qr_code && is_gcc_country) {
                $('.pos-receipt-container').addClass('sh_receipt_content')
            }
            if (_t.database.parameters.direction) {
                $('.sh_receipt_content').css('direction', 'ltr')
            }

            const date_time = new Date(self.env.pos.get_order().export_for_printing().date.isostring);


            var qr_code = this.compute_sa_qr_code(self.env.pos.company.name, self.env.pos.company.vat, date_time.toLocaleString('sv-SE'), self.env.pos.get_order().export_for_printing().total_with_tax, self.env.pos.get_order().export_for_printing().total_tax);
            if ($('#qr_image') && $('#qr_image').length > 0) {
                // Create QRCode Object

                var div = document.createElement('div')
                new QRCode(div, { text: qr_code });

                var can = $(div).find('canvas')[0]
                var img = new Image();
                img.src = can.toDataURL();

                $(img).css({ 'height': self.env.pos.config.qr_code_height, 'width': self.env.pos.config.qr_code_width })

                $('#qr_image').append(img)

            }
            super.mounted()
        }
        async _sendReceiptToCustomer() {
            super._sendReceiptToCustomer(this, arguments)
            const receiptString = this.shorderReceipt.comp.el.outerHTML;
        }
    };
    Registries.Component.extend(ReceiptScreen, PosResOrderReceipt);
    
    const PosTicketScreen = (TicketScreen) =>
    class extends TicketScreen {
    	async _onDoRefund() {
    		super._onDoRefund()
    		var self = this;
    		const order = this.getSelectedSyncedOrder();
    		if(self.env.pos.get_order().getHasRefundLines() && order && self.env.pos.config.show_return_order_ref){
    			self.env.pos.get_order().set_refunded_order_ref(order.name)
    		}
    	}
    };

    Registries.Component.extend(TicketScreen, PosTicketScreen);
    
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
    	initialize: function (attributes, options) {
            this.return_order_ref = [];
            _super_order.initialize.apply(this, arguments);
        },
        set_refunded_order_ref: function (return_order_ref) {
        	this.return_order_ref.push(return_order_ref)
        },
        get_refunded_order_ref: function () {
            return this.return_order_ref;
        },
    });
    
});
