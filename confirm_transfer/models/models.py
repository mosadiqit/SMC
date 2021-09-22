# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    is_created = fields.Boolean()

    def create_stock_picking(self):
        for rec in self:
            if not rec.is_created:
                rec.sudo().action_confirm()
                rec.sudo().button_validate()
                rec.is_created = True

