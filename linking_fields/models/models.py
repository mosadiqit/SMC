# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    do_link = fields.Char()
    invoice_link = fields.Char()


class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    purchase_link = fields.Char()


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    account_link = fields.Char()


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    stock_link = fields.Char()


class AccountPaymentInh(models.Model):
    _inherit = 'account.payment'

    payment_link = fields.Char()