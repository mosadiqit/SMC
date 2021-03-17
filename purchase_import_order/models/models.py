# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase
# from addons.purchase.models.purchase import PurchaseOrder as Purchase

class purchase_import_order(models.Model):
    _inherit= "purchase.order"
    _description = 'purchase_import_order.purchase_import_order'

    @api.model
    def _default_picking_type(self):
        return self._get_picking_type(self.env.context.get('company_id') or self.env.company.id)



    import_order= fields.Boolean(string="Import Order", default=False)
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', states=Purchase.READONLY_STATES,
                                      required=True, default=_default_picking_type,
                                      domain="['|', ('warehouse_id', '=', False), ('warehouse_id.company_id', '=', company_id)]",
                                      help="This will determine operation type of incoming shipment")


    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        if ('import_order' in vals):
            if (vals['import_order'] == True):
                sequence= self.env.ref('purchase_import_order.seq_import_order_purchase')
                vals['name']= sequence.next_by_id()

        # Ensures default picking type and currency are taken from the right company.

        # if 'get_id' not in vals or vals['get_id'] == False:
        #     sequence = self.env.ref('carpet_processing.get_id')
        #     vals['get_id'] = sequence.next_by_id()
        # return super(carpet_MenuForm, self).create(vals)

        # self_comp = self.with_company(company_id)
        # if vals.get('name', 'New') == 'New':
        #     seq_date = None
        #
        #     vals['name'] = self_comp.env['ir.sequence'].next_by_code('purchase.order', sequence_date=seq_date) or '/'
        return super(purchase_import_order, self).create(vals)

