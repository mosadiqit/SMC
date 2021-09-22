# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    def create_stock_picking(self):
        for rec in self:
            print('Hello')
            rec.sudo().action_confirm()
            rec.sudo().button_validate()

