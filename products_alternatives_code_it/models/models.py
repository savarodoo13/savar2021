from odoo import api, fields, models
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError
class ProductTemplate(models.Model):
    _inherit            = 'product.template'
    edit_part_origin    = fields.Boolean(compute="get_part",default=True)
    part_origin = fields.Char(string='Parte Original')
    def get_part(self):
        for record in self:
            if self.env.user.has_group("products_alternatives_code_it.group_edit_parte_original"):
                record.edit_part_origin = True
            else:
                record.edit_part_origin = False
class Compras(models.Model):
    _inherit = 'purchase.order'
    edit_lines = fields.Boolean(compute="get_edit",default=True)
    def get_edit(self):
        for record in self:
            if self.env.user.has_group("products_alternatives_code_it.group_edit_lineas_purchase"):
                record.edit_lines = True
            else:
                if record.state in ['done', 'cancel']:
                    record.edit_lines = False
                else:
                    record.edit_lines = True

class Compras(models.Model):
    _inherit = 'purchase.order.line'
    prioridad_it  = fields.Char('Prioridad')
    observacion_it = fields.Char('Observacion')
    #sobresescribeindo el metodo
    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        price_unit = self._get_stock_move_price_unit()
        outgoing_moves, incoming_moves = self._get_outgoing_incoming_moves()
        for move in outgoing_moves:
            qty -= move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        for move in incoming_moves:
            qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        description_picking = self.product_id.with_context(
            lang=self.order_id.dest_address_id.lang or self.env.user.lang)._get_description(
            self.order_id.picking_type_id)
        template = {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'date': self.order_id.date_order,
            'date_expected': self.date_planned,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'propagate_date': self.propagate_date,
            'propagate_date_minimum_delta': self.propagate_date_minimum_delta,
            'description_picking': description_picking,
            'propagate_cancel': self.propagate_cancel,
            'route_ids': self.order_id.picking_type_id.warehouse_id and [
                (6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
            'prioridad_it': self.prioridad_it,
            'observacion_it': self.observacion_it
        }
        diff_quantity = self.product_qty - qty
        if float_compare(diff_quantity, 0.0, precision_rounding=self.product_uom.rounding) > 0:
            po_line_uom = self.product_uom
            quant_uom = self.product_id.uom_id
            product_uom_qty, product_uom = po_line_uom._adjust_uom_quantities(diff_quantity, quant_uom)
            template['product_uom_qty'] = product_uom_qty
            template['product_uom'] = product_uom.id
            res.append(template)
        return res

class AlbaranLine(models.Model):
    _inherit      = 'stock.move'
    prioridad_it  = fields.Char('Prioridad')
    observacion_it = fields.Char('Observacion')
    trabajador_it = fields.Char("Trabajador")

    @api.model
    def default_get(self, fields):
        res = super(AlbaranLine, self).default_get(fields)

        res.update({'prioridad_it': self.purchase_line_id.prioridad_it})
        res.update({'observacion_it': self.purchase_line_id.observacion_it})        
        return res
