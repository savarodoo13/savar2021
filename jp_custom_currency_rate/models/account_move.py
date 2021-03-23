# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('invoice_date','tc_per','currency_rate','currency_id')
    def _onchange_tc_per(self):
        for line in self.line_ids:
            line._onchange_currency()
    
    @api.onchange('line_ids', 'invoice_payment_term_id', 'invoice_date_due', 'invoice_cash_rounding_id', 'invoice_vendor_bill_id')
    def _onchange_recompute_dynamic_lines(self):
        res = super(AccountMove, self)._onchange_recompute_dynamic_lines()
        if self.currency_id != self.env.user.company_id.currency_id:
            for line in self.line_ids:
                line.tc = self.currency_rate
        return res
        
    # def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
    #     res = super(AccountMove ,self)._recompute_dynamic_lines
    #     if self.currency_id != self.env.user.company_id.currency_id:
    #         for line in self.line_ids:
    #             line.tc = self.currency_rate
    #     return res

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountMoveLine, self)._onchange_product_id()
        if self.move_id.tc_per and self.move_id.currency_id != self.env.user.company_id.currency_id:
            for line in self:
                price_unit = self._get_computed_price_unit()
                line.price_unit = price_unit * (1 / self.move_id.currency_rate)
        return res
    
    @api.onchange('product_uom_id')
    def _onchange_uom_id(self):
        res = super(AccountMoveLine, self)._onchange_uom_id()
        if self.move_id.tc_per and self.move_id.currency_id != self.env.user.company_id.currency_id:
            for line in self:
                price_unit = self._get_computed_price_unit()
                line.price_unit = price_unit * (1 / self.move_id.currency_rate)
        return res
    
    @api.model
    def _get_fields_onchange_subtotal_model(self, price_subtotal, move_type, currency, company, date):
        res = super(AccountMoveLine, self)._get_fields_onchange_subtotal_model(price_subtotal, move_type, currency, company, date)
        if self.move_id.tc_per and self.move_id.currency_id != self.move_id.company_currency_id:
            if res['debit'] > 0:
                res['debit'] = res['amount_currency'] / (1 / self.move_id.currency_rate)
            else:
                res['credit'] = abs(res['amount_currency']) / (1 / self.move_id.currency_rate)
            self.tc = self.move_id.currency_rate
        else:
            if self.currency_id:
                self.tc = self.currency_id._get_conversion_rate(self.move_id.currency_id, self.env.user.company_id.currency_id, self.env.user.company_id, self.move_id.invoice_date or datetime.datetime.now())
        return res
    
    @api.onchange('amount_currency')
    def _onchange_amount_currency(self):
        res = super(AccountMoveLine, self)._onchange_amount_currency()
        if self.move_id.tc_per:
            if self.debit > 0:
                self.debit = self.amount_currency / (1 / self.move_id.currency_rate)
            else:
                self.credit = abs(self.amount_currency) / (1 / self.move_id.currency_rate)
            self.tc = self.move_id.currency_rate
        return res