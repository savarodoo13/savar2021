# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class ResCurrency(models.Model):
	_inherit = "res.currency"

	def _convert_personalize(self, from_amount, to_currency, personalize_change, company, date, round=True):
		"""Returns the converted amount of ``from_amount``` from the currency
		   ``self`` to the currency ``to_currency`` for the given ``date`` and
		   company.

		   :param company: The company from which we retrieve the convertion rate
		   :param date: The nearest date from which we retriev the conversion rate.
		   :param round: Round the result or not
		"""
		self, to_currency = self or to_currency, to_currency or self
		assert self, "convert amount from unknown currency"
		assert to_currency, "convert amount to unknown currency"
		assert company, "convert amount from unknown company"
		assert date, "convert amount from unknown date"
		# apply conversion rate
		if self == to_currency:
			to_amount = from_amount
		else:
			to_amount = from_amount * self._get_conversion_rate_personalize(self, to_currency, personalize_change, company, date)
		# apply rounding
		return to_currency.round(to_amount) if round else to_amount

	@api.model
	def _get_conversion_rate_personalize(self, from_currency, to_currency, personalize_change, company, date):
		currency_rates = (from_currency + to_currency)._get_rates(company, date)
		if to_currency.name == 'USD':
			res = (1/personalize_change) / currency_rates.get(from_currency.id)
		elif from_currency.name == 'USD':
			res = currency_rates.get(to_currency.id) / (1/personalize_change)
		else:
			res = currency_rates.get(to_currency.id) / currency_rates.get(from_currency.id)
		return res