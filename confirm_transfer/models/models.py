# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    is_created = fields.Boolean()

    def create_stock_picking(self):
	obj=self.env['stock.picking'].search([('is_created','=',False)],limit=500)
        for rec in obj:
            if not rec.is_created:
                rec.sudo().action_confirm()
                rec.sudo().button_validate()
                rec.is_created = True

