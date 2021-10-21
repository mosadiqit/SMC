# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResBranchInh(models.Model):
    _inherit = 'res.branch'

    branch_code = fields.Char('Branch Code')
    # active = fields.Boolean(default=True)


# class ResUsersInh(models.Model):
#     _inherit = 'res.users'

#     agent_code = fields.Char('Agent Code')


class ResPartnerInh(models.Model):
    _inherit = 'res.partner'

    customer_code = fields.Char('Customer Code', copy=False, index=True)
    test = fields.Boolean("Test Field")
    no_cnic = fields.Char('CNIC')
    ntn = fields.Char('NTN')
    fax = fields.Char('Fax')
    beneficiary_name = fields.Char('Beneficiary Name')
    bank_name = fields.Char('Bank Name')
    address = fields.Char('Address')
    iban_no = fields.Char('IBAN NO.')
    swift_code = fields.Char('Swift Code')
    ac_no = fields.Char('Account No.')
    short_code = fields.Char('Short Code')
    purpose = fields.Char('Purpose')
    is_supplier = fields.Boolean(default=False, compute='compute_is_supplier')
    currency_id = fields.Many2one('res.currency')

    def compute_is_supplier(self):
        for rec in self:
            rec.partner_balance = rec.credit - rec.debit
            if rec.supplier_rank > 0:
                rec.is_supplier = True
            else:
                rec.is_supplier = False

    partner_balance = fields.Float('Balance' )
    # partner_balance_1 = fields.Float('Balance', compute='compute_balance')

    # @api.depends('credit', 'debit')
    # def compute_balance(self):
    #     for rec in self:
    #         rec.partner_balance = rec.credit - rec.debit

            # partner_ledger = self.env['account.move.line'].search(
            #     [('partner_id', '=', rec.id),
            #      ('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False), ('balance', '!=', 0),
            #      ('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), '|',
            #      ('account_id.internal_type', '=', 'payable'), ('account_id.internal_type', '=', 'receivable')])
            # bal = 0
            # for par_rec in partner_ledger:
            #     bal = bal + (par_rec.debit - par_rec.credit)
            # rec.partner_balance = bal

    # @api.constrains('customer_code')
    # def check_code(self):
    #     if self.customer_code:
    #         code = self.env['res.partner'].search([('customer_code', '=', self.customer_code)])
    #         if len(code) > 1:
    #             raise UserError('User Already Exist')

    # def name_get(self):
    #     res = []
    #     for rec in self:
    #         res.append((rec.id, '%s : %s : %s' % (rec.customer_code, rec.name, str(rec.total_due))))
    #     return res

    @api.model
    def create(self, vals):
        # if vals.get('customer_code', _('New')) == _('New'):
        vals['customer_code'] = self.env['ir.sequence'].next_by_code('res.partner.sequence') or _('New')
        branch = self.env['res.branch'].browse([vals.get('branch_id')])
        vals['customer_code'] = str(1) + '-' + str(self.env.user.agent_code) + '-' + str(branch.branch_code) + vals['customer_code']
        result = super(ResPartnerInh, self).create(vals)
        return result


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    user_id = fields.Many2one('res.users', related='sale_id.user_id')
    manager_id = fields.Many2one('res.users', related='sale_id.manager_id')


class StockWarehouseInh(models.Model):
    _inherit = 'stock.warehouse'

    is_active = fields.Boolean('Active')


class StockLocationInh(models.Model):
    _inherit = 'stock.location'

    is_active = fields.Boolean('Active')


class StockMoveLineInh(models.Model):
    _inherit = 'stock.move.line'

    is_from_active = fields.Boolean('From Active')
    is_to_active = fields.Boolean('To Active', compute='compute_to_from_active')

    def compute_to_from_active(self):
        for rec in self:
            if rec.location_dest_id.is_active:
                rec.is_to_active = True
            else:
                rec.is_to_active = False



