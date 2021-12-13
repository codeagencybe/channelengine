# -*- coding: utf-8 -*-
import time, json, requests
from datetime import datetime

from odoo import models, fields, api, _
from odoo.addons.channel_engine.channel_engine_api.api import ChannelEngine
from odoo.exceptions import Warning,UserError


class ChannelengineInstace(models.Model):
    _name = "ce.instance"
    _description = "Channel Engine Instance"
    
    name = fields.Char(size=120,string='Name',required=True, help="Insert instance name")
    api_key = fields.Char('Api Key', required=True, help="Insert your channel engine API key")
    channel_shop_url = fields.Char(string='Shop URL', required=True, help="Insert channel engine shop URL")
    state = fields.Selection([('not_confirmed','Not Confirmed'),('confirmed','Confirmed')],default='not_confirmed')
    warehouse_id = fields.Many2one('stock.warehouse',string="Warehouse",help="Select warehouse for this instance")
    pricelist_id = fields.Many2one('product.pricelist',string="Pricelist")
    stock_field = fields.Many2one('ir.model.fields',string='Stock Field')
    lang_id = fields.Many2one('res.lang', string='Language')
    company_id = fields.Many2one('res.company',string="Company",help="Select company name")
    order_prefix = fields.Char(size=10, string='Order Prefix',help="Set order prefix")
    team_id = fields.Many2one('crm.team','Sales Team')
    shipment_charge_product_id = fields.Many2one("product.product","Shipment Fee",domain=[('type','=','service')])
    prod_description_erpify = fields.Many2one('ir.model.fields', 'Field for Product Description',
                                              domain=[('ttype','in', ('char', 'text')), ('model', '=', 'product.product')])
    prod_title_erpify = fields.Many2one('ir.model.fields', 'Field for Product Title',
                                        domain=[('ttype','in', ('char', 'text')), ('model', '=', 'product.product')])
    use_product_or_variants = fields.Boolean('Use Products Variants for extra data?')
    prod_temp_extra_fields_erpify = fields.Many2many('ir.model.fields', 'product_temp_ce_extra_fields_rel', string='Extra fields from Products (Template)',
                                               domain=[('ttype', 'not in', ('many2many', 'many2one', 'one2many')),
                                                       ('model', '=', 'product.product')])
    prod_extra_fields_erpify = fields.Many2many('ir.model.fields', string='Extra fields from Variants',
                                        domain=[('ttype','not in', ('many2many', 'many2one', 'one2many')), ('model', '=', 'product.product')])
    use_website_images_or_ce_images = fields.Boolean('Use Odoo Product images for Channel Product images?', default=True)
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms')
    user_id_erpify = fields.Many2one('res.users', 'Salesperson')
    #Cron
    is_auto_update_products_stock = fields.Boolean(string="Auto Update Products Stock?",default=False,help="If you want to auto update product stock so check mark True other wise False. By default it's False.")
    update_ce_stock_interval_number = fields.Integer(string='Channel Update Stock Interval Number',help="Repeat every x.")
    update_ce_stock_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], string='Channel Update Stock Interval Unit')
    update_ce_stock_next_execution = fields.Datetime(string='Channel Update Stock Next Execution', help='Next execution time')
    update_ce_stock_user_id = fields.Many2one('res.users',string="CE Update Stock",help='User')

    is_auto_update_products_price = fields.Boolean(string="Auto Update Products Price?",default=False,help="")
    update_ce_price_interval_number = fields.Integer(string='Channel Update Price Interval Number',help="Repeat every x.")
    update_ce_price_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], string='Channel Update Price Interval Unit')
    update_ce_price_next_execution = fields.Datetime(string='Channel Update Price Next Execution', help='Next execution time')
    update_ce_price_user_id = fields.Many2one('res.users',string="CE Update Price",help='User')

    is_auto_import_sales_orders = fields.Boolean(string="Auto Import Sales Orders?",default=False,help="")
    import_ce_orders_interval_number = fields.Integer(string='Channel Import Orders Interval Number',help="Repeat every x.")
    import_ce_orders_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], string='Channel Import Orders Interval Unit')
    import_ce_orders_next_execution = fields.Datetime(string='Channel Import Orders Next Execution', help='Next execution time')
    import_ce_orders_user_id = fields.Many2one('res.users',string="Channel Import Orders",help='User')

    is_auto_create_shipments = fields.Boolean(string="Auto Create Shipments?",default=False,help="")
    create_ce_shipment_interval_number = fields.Integer(string='Channel Update Shipment Interval Number',help="Repeat every x.")
    create_ce_shipment_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], string='Channel Update Shipment Interval Unit')
    create_ce_shipment_next_execution = fields.Datetime(string='Channel Update Shipment Next Execution', help='Next execution time')
    create_ce_shipment_user_id = fields.Many2one('res.users',string="CE Update Shipment",help='User')
    
    is_auto_import_ce_products = fields.Boolean(string="Auto Import Products?",default=False,help="If you want to auto import products so check mark True other wise False. By default it's False.")
    import_ce_products_interval_number = fields.Integer(string='Auto Import Products Interval Number',help="Repeat every x.")
    import_ce_products_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], string='Import product interval unit.')
    import_ce_products_next_execution = fields.Datetime(string='Auto Import Products Next Execution', help='Next execution time')
    import_ce_products_user_id = fields.Many2one('res.users',string="Auto Import Products User",help='Import product user.')
    
    is_order_confirm_to_auto_send_ack = fields.Boolean(string="Do you want to confirm sale to send ack.?",default=False,help="Checked True to auto send order acknowledgement in channel engine when channel sale order confirm.")
    

    def openerp_format_date(self, srcDate):
        srcDate = srcDate[:19]
        srcDate = time.strptime(srcDate, "%Y-%m-%dT%H:%M:%S")
        srcDate = time.strftime("%Y-%m-%d %H:%M:%S",srcDate)
        return srcDate


    def check_connection(self):
        try:
            channel_engine_obj = ChannelEngine()
            instance = self
            result = channel_engine_obj.check_connection(instance)
            if result.get('StatusCode') == 200:
                raise Warning("Service working properly")
            else:
                raise Warning("API connection has a problem please check credentials")  
        except Exception as e:
            raise Warning(str(e))
        return True
      

    def set_to_confirm(self):
        if self.state != 'confirmed' :
            try:
                channel_engine_obj = ChannelEngine()
                instance = self
                result = channel_engine_obj.check_connection(instance)
                if result.get('StatusCode') == 200:
                    self.write({'state':'confirmed'})
                else:
                    raise Warning("Given Credentials is incorrect")  
            except Exception as e:
                raise Warning(str(e))            
        return True

    def reset_to_confirm(self):
        self.write({'state': 'not_confirmed'})
        return True

    @api.model
    def auto_update_products_stock_in_channel(self, args={}):
        channel_instance_obj = self.env['ce.instance']
        channel_product_product_obj = self.env['channel.product.product']
        instance_id = args.get('instance_id')
        if instance_id:
            channel_instance_ids = channel_instance_obj.search([('state','=','confirmed'),('is_auto_update_products_stock','=',True),('id','=',instance_id)])
            for instance in channel_instance_ids:
                channel_product_product_obj.update_product_stock_in_channel(instance, False)
        return True
    
    @api.model
    def auto_update_products_price_in_channel(self, args={}):
        channel_instance_obj = self.env['ce.instance']
        channel_product_product_obj = self.env['channel.product.product']
        instance_id = args.get('instance_id')
        if instance_id:
            channel_instance_ids = channel_instance_obj.search([('state','=','confirmed'),('is_auto_update_products_price','=',True),('id','=',instance_id)])
            for instance in channel_instance_ids:
                channel_product_product_obj.update_product_price_in_channel(instance,False) 
        return True
    
    @api.model
    def auto_import_sales_orders_in_channel(self, args={}):
        channel_instance_obj = self.env['ce.instance']
        sale_order_obj = self.env['sale.order']
        instance_id = args.get('instance_id')
        if instance_id:
            channel_instance_ids = channel_instance_obj.search([('state','=','confirmed'),('is_auto_import_sales_orders','=',True),('id','=',instance_id)])    
            for instance in channel_instance_ids:
                sale_order_obj.import_sales_order_from_channel(instance) 
        return True
    
    @api.model
    def auto_create_shipment_in_channel(self, args={}):
        channel_instance_obj = self.env['ce.instance']
        sale_order_obj = self.env['sale.order']
        instance_id = args.get('instance_id')
        if instance_id:
            channel_instance_ids = channel_instance_obj.search([('state','=','confirmed'),('is_auto_create_shipments','=',True),('id','=',instance_id)])    
            for instance in channel_instance_ids:
                sale_order_obj.create_shipment_in_channel(instance) 
        return True
    
    @api.model
    def auto_imoprt_products_from_ce(self, args={}):
        channel_instance_obj = self.env['ce.instance']
        channel_product_template_obj = self.env['channel.product.template']
        instance_id = args.get('instance_id',False)
        if instance_id:
            channel_instance_id = channel_instance_obj.search([('state','=','confirmed'),('id','=',instance_id)],limit=1)    
            channel_instance_id and channel_product_template_obj.import_products_from_channel_engine(channel_instance_id[0]) 
        return True
