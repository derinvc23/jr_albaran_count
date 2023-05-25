from odoo import models, api, fields, exceptions, _
from datetime import date, datetime, time


class AlbaranCount(models.Model):
    _name="albaran.count"

    name=fields.Char(string="Nombre")
    location_id=fields.Many2one("stock.location",string="Ubicacion")
    date=fields.Datetime(string="Fecha",default=fields.Date.today())
    stock_line_ids=fields.One2many("stock.line1","albaran_id")
   
    
   
    account_deb_sal=fields.Many2one("account.account",string="Cuenta debito")
    account_cred_sal=fields.Many2one("account.account",string="Cuenta credito")
    account_deb_ent=fields.Many2one("account.account",string="Cuenta debito")
    account_cred_ent=fields.Many2one("account.account",string="Cuenta credito")

    def action_update1(self):
        location_id_d=self.env["stock.location"].search([("name","=","ajustesalida")],limit=1)
        location_id_u1=self.env["stock.location"].search([("name","=","ajusteentrada")],limit=1)
        for line in self.stock_line_ids:
            if not line.update_f and line.dif_qty>0:
                line.create_product_exit(line.product_id,line.dif_qty,self.location_id,location_id_d,self.account_cred_sal,self.account_deb_sal,line.costo)
                line.update_f=True
            elif not line.update_f and line.dif_qty<0:
                line.create_product_entry(line.product_id,abs(line.dif_qty),location_id_u1,self.location_id,self.account_cred_ent,self.account_deb_ent,line.costo)
                line.update_f=True




   
class StockLine(models.Model):
    _name="stock.line1"

    product_id=fields.Many2one("product.product",string="Producto", domain=lambda self: self.env['stock.move']._get_product_domain())
    albaran_id=fields.Many2one("albaran.count")
    codigo=fields.Char(related="product_id.default_code")
    descrip=fields.Char(related="product_id.name")
    qty=fields.Float(string="Cantidad ingresada")
    dif_qty=fields.Float(string="Diferencia",compute="get_qty",store=True)
    costo=fields.Float(related="product_id.lst_price")
    u_origen=fields.Many2one("stock.location")
    dest_origen=fields.Many2one("stock.location")
    import_t=fields.Float("Importe Total",compute="get_total")
    update_f=fields.Boolean(default=False)
    stock_move_ids = fields.One2many('stock.move', 'stcock_line1_id')

    
    @api.model
    def _get_product_domain(self):
        domain = []
        context = self.env.context
        if context.get('default_location_id'):
            domain = [('quant_ids.location_id', '=', context.get('default_location_id'))]
        return domain
    
    @api.depends("albaran_id")
    def get_qty(self):

        for line in self:
            qty=[]
            quants = self.env['stock.quant'].search([
            ('location_id', '=', line.albaran_id.location_id.id)
        ])
            for record in quants:
                if record.product_id.id==line.product_id.id:
                    qty.append(record.qty)
            if line.qty:
                line.dif_qty=sum(qty)-line.qty
            else:
                line.dif_qty=0

    def get_total(self):

        for line in self:
            
            line.import_t=line.dif_qty*line.costo

    @api.model
    def create_product_entry(self, product_id, quantity, ulocation, dlocation,credit,debit,amount):
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
            'picking_type_id': self.env["stock.picking.type"].search([("name","=","Transferencias internas")],limit=1).id,
        })

        # Confirm the product move.
        product_move.action_confirm()

        # Assign the product move.
        product_move.action_assign()

        # Process the product move.
        product_move.action_done()

        account_move = self.env['account.move'].create({
            'journal_id': self.env["account.journal"].search([("name","=","Inventario AdB")],limit=1).id,
            'ref': product_move.name,
            'date': fields.Date.today(),
           
            'line_ids': [
                (0, 0, {
                    'name': product_move.name,
                    'account_id': credit.id,
                    'debit': 0.0,
                    'credit': amount,
                }),
                (0, 0, {
                    'name': product_move.name,
                    'account_id': debit.id,
                    'debit': amount,
                    'credit': 0.0,
                }),
            ],
        })

        # Post the account move.
        account_move.post()

        # Assign the account move to the product move.
        product_move.write({
            'account_move_id': account_move.id,
        })

        return True


    @api.model
    def create_product_exit(self, product_id, quantity, ulocation, dlocation,credit,debit,amount):
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
            'picking_type_id': self.env["stock.picking.type"].search([("name","=","Transferencias internas")],limit=1).id,
        })

        # Confirm the product move.
        product_move.action_confirm()

        # Assign the product move.
        product_move.action_assign()

        # Process the product move.
        product_move.action_done()

        account_move = self.env['account.move'].create({
            'journal_id': self.env["account.journal"].search([("name","=","Inventario AdB")],limit=1).id,
            'ref': product_move.name,
            'date': fields.Date.today(),
           
            'line_ids': [
                (0, 0, {
                    'name': product_move.name,
                    'account_id': credit.id,
                    'debit': 0.0,
                    'credit': amount,
                }),
                (0, 0, {
                    'name': product_move.name,
                    'account_id': debit.id,
                    'debit': amount,
                    'credit': 0.0,
                }),
            ],
        })

        # Post the account move.
        account_move.post()

        # Assign the account move to the product move.
        product_move.write({
            'account_move_id': account_move.id,
        })

        return True

   


class StockLocation(models.Model):
    _inherit = 'stock.location'

    def get_warehouse(self):
        """
        Get the warehouse that owns this location.
        """
        warehouse = self.env['stock.warehouse'].search([('lot_stock_id', '=', self.id)], limit=1)
        return warehouse

class StockMove(models.Model):
    _inherit = 'stock.move'

    stcock_line1_id=fields.Many2one("stock.line1")

    @api.model
    def _get_product_domain(self):
        domain = []
        if self.location_id:
            domain = [('quant_ids.location_id', '=', self.location_id.id)]
        return domain