# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    is_service_charges_added = fields.Boolean(default=False)

    def remove_service_products(self):
        for rec in self.order_line:
            if rec.product_id.type == 'service' or rec.name == 'Services Charges':
                rec.unlink()
        self.is_service_charges_added = False

    def add_products(self):
        seq = 0
        for rec in self.order_line:
            seq = rec.sequence
        section_values = []
        val = (0, 0, {'display_type': 'line_section', 'name': 'Services Charges', 'sequence': seq + 1})
        section_values.append(val)
        self.update({'order_line': section_values})
        self.get_service_charges_products(seq)
        self.is_service_charges_added = True

    def get_service_charges_products(self, seq):
        products = self.env['product.product'].search([('is_installation_charges', '=', True)])
        price_unit = self.get_price_unit()
        i = 1
        for product in products:
            self.env['sale.order.line'].create({
                'order_id': self.id,
                'product_id': product.id,
                'name': product.name,
                'product_uom_qty': 1,
                'price_unit': price_unit if product.name == 'Installation Charges' else 0,
                'sequence': seq + 1
            })
            i += 1

    def get_price_unit(self):
        sum = 0
        for rec in self.order_line:
            if rec.product_id.type != 'service':
                sum = sum + (rec.product_id.installation_charges * rec.product_uom_qty)
            if rec.product_id.name == 'Installation Charges':
                rec.price_unit = sum
            else:
                if rec.product_id.type == 'service':
                    rec.price_unit = 0
                else:
                    rec.price_unit = rec.product_id.lst_price
        return sum


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    is_installation_charges = fields.Boolean('Installation Charges')
    installation_charges = fields.Float('Installation Charges')


class SaleOrderlineInh(models.Model):
    _inherit = 'sale.order.line'

    # is_service_product = fields.Boolean()

    @api.onchange('price_unit')
    def onchange_unit_price(self):
        for rec in self:
            if rec.env.user.has_group('smc_service_charges.group_readonly_unit_price_user'):
                if rec.product_id.type != 'service':
                    if rec.price_unit:
                        raise UserError('You Cannot Change Product Price!')

