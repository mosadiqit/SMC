# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    customer_balance = fields.Float('Balance', compute='compute_customer_balance')

    def compute_customer_balance(self):
        for rec in self:
            invoices = self.env['res.partner'].search([('id', '=', rec.partner_id.id)])
            rec.customer_balance = invoices.total_due


class StockLandedInh(models.Model):
    _inherit = 'stock.landed.cost'

    vendor_bill_ids = fields.Many2many('account.move')

    def action_show_line(self):
        vals_list = []
        for rec in self.vendor_bill_ids:
            for line in rec.invoice_line_ids:
                vals_list.append([0, 0, {
                    'account_id': line.account_id.id,
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'price_unit': line.price_unit,
                    'split_method': 'equal',
                }])
        self.cost_lines = vals_list
