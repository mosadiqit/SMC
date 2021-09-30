
from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    partner_balance = fields.Float('Balance', compute='compute_balance')

    def compute_balance(self):
        print('Hello')
        partner_ledger = self.env['account.move.line'].search(
            [('partner_id', '=', self.partner_id.id),
             ('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False), ('balance', '!=', 0),
             ('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), '|',
             ('account_id.internal_type', '=', 'payable'), ('account_id.internal_type', '=', 'receivable')])
        bal = 0
        for par_rec in partner_ledger:
            bal = bal + (par_rec.debit - par_rec.credit)
        self.partner_balance = bal
