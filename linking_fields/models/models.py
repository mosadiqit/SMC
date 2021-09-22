# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    do_link = fields.Char()
    invoice_link = fields.Char("Invoice link")
    cus_invoice_link = fields.Many2one("account.move", "Sale Order", compute="_compute_the_invoice_link")
    qty_invoice_link = fields.Integer("Sale Order QTY", compute="_compute_the_invoice_link")

    cus_do_link = fields.Many2one("stock.picking", "Stock Picking", compute="_compute_the_do_link")
    qty_do_link = fields.Integer("DO QTY", compute="_compute_the_do_link")

    def _compute_the_do_link(self):
        for i in self:
            obj = self.env["stock.picking"].search([("stock_link", '=', i.client_order_ref)], limit=1)
            print(obj.stock_link)
            i.cus_do_link = obj.id
            i.qty_do_link = len(self.env["stock.picking"].search([("stock_link", '=', i.client_order_ref)]))

    def smart_delivery_button(self):
        return {
            'name': _('Picking'),
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('stock_link', '=', self.client_order_ref)],
            'type': 'ir.actions.act_window',
        }

    def _compute_the_invoice_link(self):
        for i in self:
            obj = self.env["account.move"].search([("account_link", '=', i.client_order_ref)],limit=1)
            i.qty_invoice_link=len(self.env["account.move"].search([("account_link", '=', i.client_order_ref)]))
            i.cus_invoice_link = obj.id

    def smart_invoice_button(self):
        return {
            'name': _('Invoices'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('account_link', '=', self.client_order_ref)],
            'type': 'ir.actions.act_window',
        }


class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    purchase_link = fields.Char("Receipt Link")
    bill_link = fields.Char("Bill Link")
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To')


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    account_link = fields.Char()
    purchase_link = fields.Char("Purchase Order")
    cus_so_link = fields.Many2one("sale.order", "Sale Order",compute="_compute_the_invoice_link")
    qty_account_link = fields.Integer("Sale Order QTY",compute="_compute_the_invoice_link")

    def _compute_the_invoice_link(self):
        for i in self:
            obj = self.env["sale.order"].search([("client_order_ref", '=', i.account_link)],limit=1)
            i.cus_so_link = obj.id
            i.qty_account_link=len(self.env["sale.order"].search([("client_order_ref", '=', i.account_link)]))

    def smart_sale_order_button(self):
        return {
            'name': _('Sale order'),
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('client_order_ref', '=', self.account_link)],
            'type': 'ir.actions.act_window',
        }


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    stock_link = fields.Char()
    purchase_link = fields.Char("Purchase Order")

    cus_do_link = fields.Many2one("sale.order", "Sale Order", compute="_compute_the_do_link")
    qty_do_link = fields.Integer("SO QTY", compute="_compute_the_do_link")

    def _compute_the_do_link(self):
        for i in self:
            obj = self.env["sale.order"].search([("client_order_ref", '=', i.stock_link)], limit=1)
            i.cus_do_link = obj.id
            i.qty_do_link = len(self.env["sale.order"].search([("client_order_ref", '=', i.stock_link)]))


class AccountPaymentInh(models.Model):
    _inherit = 'account.payment'

    payment_link = fields.Char()
