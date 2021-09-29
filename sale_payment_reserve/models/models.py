# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    payment_count = fields.Integer(compute='compute_payments')
    # delivery_date = fields.Date('Delivery Date')
    commitment_date = fields.Datetime('Delivery Date', copy=False,
                                      states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
                                      help="This is the delivery date promised to the customer. "
                                           "If set, the delivery order will be scheduled based on "
                                           "this date rather than product lead times.")

    @api.depends('name')
    def compute_payments(self):
        for rec in self:
            count = self.env['account.payment'].search_count([('ref', '=', rec.name)])
            rec.payment_count = count

    def action_register_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Apply Advance Payments',
            'view_id': self.env.ref('sale_payment_reserve.view_advance_payment_wizard_form', False).id,
            'context': {'default_ref': self.name, 'default_order_amount': self.amount_total, 'default_user_id': self.user_id.id},
            'target': 'new',
            'res_model': 'advance.payment.wizard',
            'view_mode': 'form',
        }

    def action_show_payments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Advance Payments',
            'view_id': self.env.ref('account.view_account_payment_tree', False).id,
            'target': 'current',
            'domain': [('ref', '=', self.name)],
            'res_model': 'account.payment',
            'views': [[False, 'tree'], [False, 'form']],
        }

    def action_confirm(self):
        res = super(SaleOrderInh, self).action_confirm()
        for order in self:
            for picking in order.picking_ids:
                picking.do_unreserve()
        return res


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('manager_approval', 'Credit Approval from Manager'),
        ('ceo_approval', 'Credit Approval from CEO'),
        ('reserve_manager_approvals', 'Reserve Extension Approval from Manager'),
        ('reserve_ceo_approval', 'Reserve Extension Approval from CEO'),
        ('duration_manager_approvals', 'Duration Approval from Manager'),
        ('duration_ceo_approval', 'Duration Approval from CEO'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")
    no_enough_amount = fields.Boolean(default=False, compute='compute_payment')
    is_approved_by_manager = fields.Selection([
        ('none', 'None'),
        ('manager', 'Reserve Approved By Manager'), ], string='Reserve Approved By Manager', default='none')
    is_approved_by_ceo = fields.Selection([
        ('none', 'None'),
        ('ceo', 'Reserve Approved By CEO'), ], string='Reserve Approved By CEO', default='none')

    def action_test(self):
        self.is_approved_by_manager = 'manager'
        self.state = 'duration_ceo_approval'

    # is_approved_by_manager = fields.Boolean('Reserve Approved By Manager')
    # is_approved_by_ceo = fields.Boolean('Reserve Approved By CEO')

    # is_approved_by_manager_credit = fields.Boolean('Credit Approved By Manager')
    # is_approved_by_ceo_credit = fields.Boolean('Credit Approved By CEO')

    is_approved_by_manager_credit = fields.Selection([
        ('none', 'None'),
        ('manager', 'Credit Approved By Manager'), ], string='Credit Approved By Manager', default='none')
    is_approved_by_ceo_credit = fields.Selection([
        ('none', 'None'),
        ('ceo', 'Credit Approved By CEO'), ], string='Credit Approved By CEO', default='none')

    def action_reject(self):
        self.state = 'confirmed'

    def action_duration_manager_approval(self):
        self.is_approved_by_manager = 'manager'
        self.state = 'duration_ceo_approval'

    def action_duration_ceo_approval(self):
        self.is_approved_by_ceo = 'ceo'
        self.action_assign()

    @api.depends('sale_id.amount_total')
    def compute_payment(self):
        for rec in self:
            partner = self.env['res.partner'].search([('id', '=', rec.partner_id.id)])
            partner_ledger = self.env['account.move.line'].search(
                [('partner_id', '=', partner.id),
                 ('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False), ('balance', '!=', 0),
                 ('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), '|',
                 ('account_id.internal_type', '=', 'payable'), ('account_id.internal_type', '=', 'receivable')])
            bal = 0
            for par_rec in partner_ledger:
                bal = bal + (par_rec.debit - par_rec.credit)
            if partner:
                if -(bal) >= (rec.sale_id.amount_total / 2):
                    rec.no_enough_amount = False
                else:
                    rec.no_enough_amount = True
            else:
                rec.no_enough_amount = False

    def action_reserve_do(self):
        flag = 0
        for rec in self:
            if rec.picking_type_id.code == 'outgoing':
                partner = self.env['res.partner'].search([('id', '=', rec.partner_id.id)])
                partner_ledger = self.env['account.move.line'].search(
                    [('partner_id', '=', partner.id),
                     ('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False), ('balance', '!=', 0),
                     ('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), '|', ('account_id.internal_type', '=', 'payable'),('account_id.internal_type', '=', 'receivable')])
                bal = 0
                for par_rec in partner_ledger:
                    bal = bal + (par_rec.debit - par_rec.credit)
                if partner:
                    if -(bal) >= (rec.sale_id.amount_total/2):
                        if not rec.sale_id.commitment_date:
                            rec.sale_id.commitment_date = datetime.today() + relativedelta(days=3)
                        if abs((rec.sale_id.commitment_date.date() - datetime.today().date()).days) <= 7:
                            rec.action_assign()
                            flag = 1
                        else:
                            rec.state = 'duration_manager_approvals'
                    else:
                        raise UserError('There is no enough Advance Payment available to Reserve this DO.')
                else:
                    raise UserError('There is no enough Advance Payment available to Reserve this DO.')
            else:
                rec.action_assign()

    def action_manager_approval(self):
        self.is_approved_by_manager_credit = 'manager'
        self.state = 'ceo_approval'

    def action_ceo_approval(self):
        self.is_approved_by_ceo_credit = 'ceo'
        self.action_assign()

    def action_get_approvals(self):
        self.state = 'manager_approval'


class AccountPaymentInh(models.Model):
    _inherit = 'account.payment'

    user_id = fields.Many2one('res.users', related="partner_id.user_id")
