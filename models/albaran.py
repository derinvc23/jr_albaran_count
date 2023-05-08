from odoo import models, api, fields, exceptions, _
from datetime import date, datetime, time


class AlbaranCount(models.Model):
    _name="albaran.count"

    name=fields.Char(string="Nombre")
    stock_id=fields.Many2one("stock.picking",string="Albaran")
    date=fields.Datetime(string="Fecha",default=fields.Date.today())
    stock_line_ids=fields.One2many("stock.line1","albaran_id")

    def action_update1(self):
        for line in self.stock_line_ids:
            if not line.update_f and line.dif_qty>0:
                line.create_product_exit(line.product_id,line.dif_qty,line.u_origen,line.dest_origen)
                line.update_f=True
            elif not line.update_f and line.dif_qty<0:
                line.create_product_entry(line.product_id,abs(line.dif_qty),line.u_origen,line.dest_origen)
                line.update_f=True




   
class StockLine(models.Model):
    _name="stock.line1"

    product_id=fields.Many2one("product.product",string="Producto")
    albaran_id=fields.Many2one("albaran.count")
    codigo=fields.Char(related="product_id.default_code")
    descrip=fields.Char(related="product_id.name")
    qty=fields.Float(string="Cantidad ingresada")
    dif_qty=fields.Float(string="Diferencia",compute="get_qty")
    costo=fields.Float(related="product_id.lst_price")
    u_origen=fields.Many2one("stock.location",compute="get_u_o")
    dest_origen=fields.Many2one("stock.location",compute="get_u_d")
    import_t=fields.Float("Importe Total",compute="get_total")
    update_f=fields.Boolean(default=False)

    def get_u_o(self):
        for line in self:
            line.u_origen=line.albaran_id.stock_id.location_id.id
    def get_u_d(self):
        for line in self:
            line.dest_origen=line.albaran_id.stock_id.location_dest_id.id

    def get_qty(self):

        for line in self:
            qty=[]
            for record in line.albaran_id.stock_id.move_lines:
                if record.product_id.id==line.product_id.id:
                    qty.append(record.product_uom_qty)
            if line.qty:
                line.dif_qty=sum(qty)-line.qty
            else:
                line.dif_qty=0

    def get_total(self):

        for line in self:
            
            line.import_t=line.dif_qty*line.costo

    @api.model
    def create_product_entry(self, product_id, quantity, ulocation, dlocation):
        """This function creates a product entry in the warehouse."""

        warehouse1 = self.env['stock.warehouse'].search([('lot_stock_id', '=', self.dest_origen.id)], limit=1)
        # Get the warehouse location.
        location_id = self.env.ref('stock.stock_location_stock')
        #input_location = warehouse.view_location_id.child_ids.filtered(lambda r: r.usage == 'internal' and r.location_id.usage == 'supplier').id
        warehouse=location_id.get_warehouse()

        # Create the product move object.
        product_move = self.env['stock.move'].create({
            'name': product_id.name,
            'product_id': product_id.id,
            'product_uom_qty': quantity,
            'product_uom': product_id.uom_id.id,
            'location_id': dlocation.id,
            'location_dest_id':ulocation.id,
            'picking_type_id': warehouse.in_type_id.id,
        })

        # Confirm the product move.
        product_move.action_confirm()

        # Assign the product move.
        product_move.action_assign()

        # Process the product move.
        product_move.action_done()

        return True


    @api.model
    def create_product_exit(self, product_id, quantity, ulocation, dlocation):
        """This function creates a product exit from the warehouse."""

        # Get the warehouse location.
        warehouse1 = self.env['stock.warehouse'].search([('lot_stock_id', '=', self.dest_origen.id)], limit=1)
        #input_location = warehouse.view_location_id.child_ids.filtered(lambda r: r.usage == 'internal' and r.location_id.usage == 'supplier').id
        location_id = self.env.ref('stock.stock_location_stock')
       
        warehouse=location_id.get_warehouse()
        # Create the product move object.
        product_move = self.env['stock.move'].create({
            'name': product_id.name,
            'product_id': product_id.id,
            'product_uom_qty': quantity,
            'product_uom': product_id.uom_id.id,
            'location_id': ulocation.id,
            'location_dest_id':dlocation.id,
            'picking_type_id': warehouse.out_type_id.id,
        })

        # Confirm the product move.
        product_move.action_confirm()

        # Assign the product move.
        product_move.action_assign()

        # Process the product move.
        product_move.action_done()

        return True

   


class StockLocation(models.Model):
    _inherit = 'stock.location'

    def get_warehouse(self):
        """
        Get the warehouse that owns this location.
        """
        warehouse = self.env['stock.warehouse'].search([('lot_stock_id', '=', self.id)], limit=1)
        return warehouse
