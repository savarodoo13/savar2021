# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError

class DeleteReversedMove(models.TransientModel):
	_name = "delete.reversed.move"

	def delete_reversed_moves(self):
		
		self._cr.execute('''
			SELECT ID,REVERSED_ENTRY_ID FROM ACCOUNT_MOVE 
			WHERE (REVERSED_ENTRY_ID IS NOT NULL AND TYPE = 'entry' AND COMPANY_ID = %s AND JOURNAL_ID = %s) ORDER BY ID
		''' % (str(self.env.company.id),str(self.env.company.currency_exchange_journal_id.id)))

		for row in self._cr.fetchall():
			reversed_move = self.env['account.move'].browse(row[1])
			move = self.env['account.move'].browse(row[0])

			for mm in move.line_ids:
				mm.remove_move_reconcile()
			move.button_cancel()
			move.line_ids.unlink()
			move.name = "/"
			move.unlink()

			reversed_move.button_cancel()
			reversed_move.line_ids.unlink()
			reversed_move.name = "/"
			reversed_move.unlink()

		return self.env['popup.it'].get_message('SE ELIMINARON LOS ASIENTOS DE REVERSION DE MANERA CORRECTA.')