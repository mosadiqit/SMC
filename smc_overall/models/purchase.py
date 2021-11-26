
from odoo import models, fields, api, _


class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    status_ref = fields.Selection([
        ('in_production', 'In Production'),
        ('on_the_way', 'On the Way to Khi'),
        ('out_of_way', 'Out of way to Lhr'),
        ('arrived', 'Arrived'),
        ('custom', 'Custom'),
    ], string='Status Ref')

    manual_status = fields.Char('Manual Status')