# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from itertools import groupby
from odoo.tools.float_utils import float_is_zero
from lxml import etree


class SMC(models.Model):
    _inherit = 'product.template'

    sale_discontinued = fields.Boolean("Sales Discontinued Products", compute="_compute_on_hand", store=True)

    @api.depends('qty_available', 'purchase_ok', 'sale_ok')
    def _compute_on_hand(self):
        for i in self:
            if i.type == 'product':
                print(i.sale_ok)
                if not i.sale_ok or not i.purchase_ok:
                    i.sale_discontinued = True

            #     if i.qty_available <= 0 and i.purchase_ok == False:
            #         i.sale_discontinued = True
            #         i.sale_ok = False
            #     elif i.qty_available > 0 and i.purchase_ok == False:
            #         i.sale_discontinued = True
            #         i.sale_ok = True
            #     else:
            #         i.sale_ok = True
            #         i.sale_discontinued = False
            # else:
            #     i.sale_discontinued = False


class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    def action_view_invoices(self):
        """This function returns an action that display existing vendor bills of
        given purchase order ids. When only one found, show the vendor bill
        immediately.
        """
        invoices = self.env['account.move'].search([('invoice_origin', '=', self.name)])
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the purchase order, we read them in sudo to fill the
            # cache.
            self.sudo()._read(['invoice_ids'])
            invoices = self.invoice_ids

        result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        # choose the view_mode accordingly
        if len(invoices) > 1:
            result['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = invoices.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    def action_create_invoice(self):
        """Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        # 1) Prepare invoice vals and clean-up the section lines
        invoice_vals_list = []
        for order in self:
            if order.invoice_status != 'to invoice':
                continue

            order = order.with_company(order.company_id)
            pending_section = None
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    if pending_section:
                        invoice_vals['invoice_line_ids'].append((0, 0, pending_section._prepare_account_move_line()))
                        pending_section = None
                    invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_account_move_line()))
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        # 2) group by (company_id, partner_id, currency_id) for batch creation
        new_invoice_vals_list = []
        for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (x.get('company_id'), x.get('partner_id'), x.get('currency_id'))):
            origins = set()
            payment_refs = set()
            refs = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                origins.add(invoice_vals['invoice_origin'])
                payment_refs.add(invoice_vals['payment_reference'])
                refs.add(invoice_vals['ref'])
            ref_invoice_vals.update({
                'ref': ', '.join(refs)[:2000],
                'invoice_origin': ', '.join(origins),
                'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
            })
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)
        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        moves.filtered(lambda m: m.currency_id.round(m.amount_total) < 0).action_switch_invoice_into_refund_credit_note()
        return self.action_view_invoices()


class in_invoicing(models.Model):
    _inherit = 'account.move'

    delivery_order = fields.Many2one('stock.picking', compute='_compute_global')
    create_user = fields.Many2one('res.users', string='User', compute="compute_self_id")
    sale_origin = fields.Many2one('sale.order', compute='_compute_sale_origin')
    purchase_origin = fields.Many2one('purchase.order',  compute='_compute_purchase_origin')

    def _compute_purchase_origin(self):
        for i in self:
            record = self.env['purchase.order'].search([('name', '=', i.invoice_origin)], limit=1)
            i.purchase_origin = record.id

    def _compute_sale_origin(self):
        for i in self:
            record = self.env['sale.order'].search([('name', '=', i.invoice_origin)], limit=1)
            i.sale_origin = record.id

    def compute_self_id(self):
        for i in self:
            i.create_user = i.env.uid

    def _compute_global(self):
        for i in self:
            record = self.env['stock.picking'].search([('origin', '=', i.invoice_origin)], limit=1)
            i.delivery_order = record.id


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('manager', 'Discount Approval from Manager'),
        ('ceo', 'Discount Approval from CEO'),
        ('confirmed', 'Approved'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    max_discount = fields.Float(string='Max Disccount', compute='compute_max_disccount', default=0, store=True)
    allowed_discount = fields.Float(string='Allowed Disccount', related='create_user.allowed_discount')
    create_user = fields.Many2one('res.users', string='User', default=lambda self:self.env.user.id, compute='compute_self_id')
    is_approved_by_manager_discount = fields.Selection([
        ('none', 'None'),
        ('manager', 'Discount Approved By Manager'),], string='Discount Approved By Manager', default='none')
    is_approved_by_ceo_discount = fields.Selection([
        ('none', 'None'),
        ('ceo', 'Discount Approved By CEO'), ], string='Discount Approved By CEO', default='none')

    def action_manager_approve(self):
        for sale_order in self:
            if sale_order.max_discount > sale_order.allowed_discount:
                raise UserError(
                    _('Your discount limit is lesser then allowed discount.Click on "Ask for Approval" for Approvals'))
            if sale_order.global_discount_type == 'percent':
                if sale_order.global_order_discount > sale_order.allowed_discount:
                    raise UserError('Global Discount Should be Less than Allowed Discount')

            else:
                amount = (sale_order.allowed_discount / 100) * sale_order.amount_untaxed
                if sale_order.global_order_discount > amount:
                    raise UserError('Global Discount Should be Less than Allowed Discount')
            sale_order.is_approved_by_manager_discount = 'manager'
            sale_order.state = 'confirmed'

    def action_ceo_approve(self):
        for sale_order in self:
            if sale_order.max_discount > sale_order.allowed_discount:
                raise UserError(
                    _('Your discount limit is lesser then allowed discount.Click on "Ask for Approval" for Approvals'))
            if sale_order.global_discount_type == 'percent':
                if sale_order.global_order_discount > sale_order.allowed_discount:
                    raise UserError('Global Discount Should be Less than Allowed Discount')

            else:
                amount = (sale_order.allowed_discount / 100) * sale_order.amount_untaxed
                if sale_order.global_order_discount > amount:
                    raise UserError('Global Discount Should be Less than Allowed Discount')
            sale_order.is_approved_by_ceo_discount = 'ceo'
            sale_order.state = 'confirmed'

    def action_reject(self):
        self.state = 'draft'

    def compute_self_id(self):
        for i in self:
            i.create_user = i.env.user.id

    def from_manager_approval(self):
        self.state = 'manager'

    def from_ceo_approval(self):
        self.state = 'ceo'

    def action_confirm(self):
        for sale_order in self:
            if sale_order.max_discount > sale_order.allowed_discount:
                raise UserError(
                    _('Your discount limit is lesser then allowed discount.Click on "Ask for Approval" for Approvals'))
            if sale_order.global_discount_type == 'percent':
                if sale_order.global_order_discount > sale_order.allowed_discount:
                    raise UserError('Global Discount Should be Less than Allowed Discount')

            else:
                amount = (sale_order.allowed_discount / 100) * sale_order.amount_untaxed
                if sale_order.global_order_discount > amount:
                    raise UserError('Global Discount Should be Less than Allowed Discount')

            # partner_ledger = self.env['account.move.line'].search(
            #     [('partner_id', '=', sale_order.partner_id.id),
            #      ('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False), ('balance', '!=', 0),
            #      ('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), '|',
            #      ('account_id.internal_type', '=', 'payable'), ('account_id.internal_type', '=', 'receivable')])
            # existing_deliveries = self.env['stock.picking'].search([('partner_id', '=', sale_order.partner_id.id), ('state', '=', 'assigned')])
            # existing_bal = 0
            # for delivery in existing_deliveries:
            #     existing_bal = existing_bal + delivery.sale_id.amount_total
            # acc_bal = 0
            # for par_rec in partner_ledger:
            #     acc_bal = acc_bal + (par_rec.debit - par_rec.credit)
            # acc_bal = -(acc_bal) - existing_bal
            # if acc_bal < ((sale_order.amount_total * 75) / 100):
            #     raise UserError('No Enough Amount in Account')
        return super(SaleOrder, self).action_confirm()

    @api.depends("order_line.discount")
    def compute_max_disccount(self):
        for i in self:
            maximum = []
            diss = 0.0
            for rec in i.order_line:
                maximum.append(rec.discount)
            if maximum:
                diss = max(maximum)
            i.max_discount = diss


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_above = fields.Boolean('Above Discount')

    @api.onchange('discount')
    def onchange_discount(self):
        for rec in self:
            if rec.discount > rec.order_id.allowed_discount:
                rec.is_above = True
            else:
                rec.is_above = False


class users_inherit(models.Model):
    _inherit = 'res.users'
    _description = 'adding to users table'

    allowed_discount = fields.Float(string='Discount Allowed')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    shipping_address = fields.Char(string='Shipping Address', related='partner_id.street')
    partner_mobile = fields.Char(string='Mobile', related='partner_id.mobile')
    create_user = fields.Many2one('res.users', string='User', compute="compute_self_id")
    invoice_origin = fields.Many2one('account.move', compute='_compute_invoice_origin')
    show_origin = fields.Boolean('Show Origin', compute='compute_show_origin')

    @api.depends('sale_id', 'purchase_id')
    def compute_show_origin(self):
        for rec in self:
            if rec.purchase_id:
                rec.show_origin = True
            elif rec.sale_id:
                rec.show_origin = False
            else:
                rec.show_origin = False

    def _compute_invoice_origin(self):
        for i in self:
            record = self.env['account.move'].search([('invoice_origin', '=', i.origin), ('state', '=', 'posted')], limit=1)
            i.invoice_origin = record.id

    def compute_self_id(self):
        for i in self:
            i.create_user = i.sale_id.user_id.id
