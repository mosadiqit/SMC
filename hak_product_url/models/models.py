# -*- coding: utf-8 -*-

from odoo import models, fields, api
import xml.etree.ElementTree as ET


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    url = fields.Char(string='URL')


    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProductTemplate, self).create(vals_list)
        res.create_product_url()
        return res

    def create_product_url(self):
        attachment_obj = self.env['ir.attachment']
        if not self.url:
            attachment_id = attachment_obj.sudo().create(
                {'name': self.name, 'type': 'binary', 'datas': self.image_1920, 'public': 1})
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url') + attachment_id.local_url+".png"
            self.url = base_url



    def server_create_product_url(self):
        attachment_obj = self.env['ir.attachment']
        for i in self:
            if i.image_1920:
                if not i.url:
                    attachment_id = attachment_obj.sudo().create(
                        {'name': i.name, 'type': 'binary', 'datas': i.image_1920, 'public': 1})
                    base_url = self.env['ir.config_parameter'].sudo().get_param(
                        'web.base.url') + attachment_id.local_url+".png"
                    i.url = base_url
