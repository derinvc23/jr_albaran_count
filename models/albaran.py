from odoo import models, api, fields, exceptions, _
from datetime import date, datetime, time


class AlbaranCount(models.Model):
    _name="albaran.count"

    name=fields.Char(string="Nombre")
    stock_id=fields.Many2one("stock.picking",string="Albaran")
    date=fields.Datetime(string="Fecha",default=fields.Date.today())
    stock_line_ids=fields.One2many("stock.line1","albaran_id")


   
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






