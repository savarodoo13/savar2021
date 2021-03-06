# -*- coding: utf-8 -*-

from odoo import models, fields, api
import string
from copy import copy
from io import StringIO, BytesIO
import base64
from reportlab.platypus import Image
from decimal import *
from string import ascii_lowercase
import itertools

class ReportBase(models.Model):
	_name = 'report.base'

	#Function to round UP numbers like 2.5 'cause in python this kind of rounding always go down
	def custom_round(self, number, decimals=False):
		if decimals and type(decimals) is int and decimals > 0:
			factor = '0' * decimals
			return float(Decimal(str(number)).quantize(Decimal('.%s' % factor), rounding=ROUND_HALF_UP))
		else:
			return float(Decimal(str(number)).quantize(Decimal('1.'), rounding=ROUND_HALF_UP))

	#Function to return Image parse from binary to Image
	def create_image(self, image, route, width, height):
		try:
			tmp = open(route, 'wb+')
			tmp.write(base64.b64decode(image))
			tmp.close()
			return Image(route, width, height)
		except:
			return False

	#Function to generate headers for excel file#
	def get_headers(self,worksheet,headers,x,y,cell_format):
		for c,head in enumerate(headers):
			worksheet.write(x,y,headers[c],cell_format)
			y += 1
		return worksheet

	#Function to set widths for 52 maximum cells#
	def resize_cells(self,worksheet,widths):
		CELLS=[]
		for s in itertools.islice(self.iter_all_strings(), 75):
			CELLS.append(s.upper())
		for c,width in enumerate(widths):
			worksheet.set_column('%s:%s' % (CELLS[c],CELLS[c]), width)
		return worksheet

	def iter_all_strings(self):
		size = 1
		while True:
			for s in itertools.product(ascii_lowercase, repeat=size):
				yield "".join(s)
			size +=1

	def get_formats(self,workbook):
		formats = {}

		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_size(10.5)
		boldbord.set_bg_color('#DCE6F1')
		boldbord.set_font_name('Times New Roman')
		formats['boldbord'] = boldbord

		especial1 = workbook.add_format()
		especial1.set_align('justify')
		especial1.set_align('vcenter')
		especial1.set_border(style=1)
		especial1.set_text_wrap()
		especial1.set_font_size(10)
		especial1.set_font_name('Times New Roman')
		formats['especial1'] = especial1

		especial2 = workbook.add_format({'bold': True})
		especial2.set_align('justify')
		especial2.set_align('vcenter')
		especial2.set_text_wrap()
		especial2.set_font_size(11)
		especial2.set_font_name('Times New Roman')
		formats['especial2'] = especial2

		especial3 = workbook.add_format({'bold': True})
		especial3.set_align('center')
		especial3.set_align('vcenter')
		especial3.set_border(style=1)
		especial3.set_text_wrap()
		especial3.set_bg_color('#DCE6F1')
		especial3.set_font_size(15)
		especial3.set_font_name('Times New Roman')
		formats['especial3'] = especial3

		especial4 = workbook.add_format()
		especial4.set_align('justify')
		especial4.set_align('vcenter')
		especial4.set_text_wrap()
		especial4.set_font_size(11)
		especial4.set_font_name('Times New Roman')
		formats['especial4'] = especial4

		especial5 = workbook.add_format({'bold': True})
		especial5.set_align('center')
		especial5.set_align('vcenter')
		especial5.set_text_wrap()
		especial5.set_font_size(14)
		especial5.set_font_name('Times New Roman')
		formats['especial5'] = especial5

		especialdate = workbook.add_format({'num_format':'yyyy-mm-dd'})
		especialdate.set_align('justify')
		especialdate.set_align('vcenter')
		especialdate.set_font_size(11)
		especialdate.set_font_name('Times New Roman')
		formats['especialdate'] = especialdate

		numberdosespecial = workbook.add_format({'num_format':'0.00'})
		numberdosespecial.set_align('right')
		numberdosespecial.set_align('vcenter')
		numberdosespecial.set_font_size(11)
		numberdosespecial.set_font_name('Times New Roman')
		formats['numberdosespecial'] = numberdosespecial

		numbercuatro = workbook.add_format({'num_format':'0.0000'})
		numbercuatro.set_align('right')
		numbercuatro.set_align('vcenter')
		numbercuatro.set_border(style=1)
		numbercuatro.set_font_size(10)
		numbercuatro.set_font_name('Times New Roman')
		formats['numbercuatro'] = numbercuatro

		numberdos = workbook.add_format({'num_format':'0.00'})
		numberdos.set_align('right')
		numberdos.set_align('vcenter')
		numberdos.set_border(style=1)
		numberdos.set_font_size(10)
		numberdos.set_font_name('Times New Roman')
		formats['numberdos'] = numberdos

		number = workbook.add_format({'num_format':'0'})
		number.set_align('right')
		number.set_align('vcenter')
		number.set_border(style=1)
		number.set_font_size(10)
		number.set_font_name('Times New Roman')
		formats['number'] = number

		numbertotal = workbook.add_format({'num_format':'0.00','bold': True})
		numbertotal.set_align('right')
		numbertotal.set_align('vcenter')
		numbertotal.set_border(style=1)
		numbertotal.set_font_size(10.5)
		numbertotal.set_font_name('Times New Roman')
		numbertotal.set_underline()
		formats['numbertotal'] = numbertotal

		dateformat = workbook.add_format({'num_format':'yyyy-mm-dd'})
		dateformat.set_align('justify')
		dateformat.set_align('vcenter')
		dateformat.set_border(style=1)
		dateformat.set_font_size(10)
		dateformat.set_font_name('Times New Roman')
		formats['dateformat'] = dateformat

		reverse_dateformat = workbook.add_format({'num_format':'dd-mm-yyyy'})
		reverse_dateformat.set_align('justify')
		reverse_dateformat.set_align('vcenter')
		reverse_dateformat.set_border(style=1)
		reverse_dateformat.set_font_size(10)
		reverse_dateformat.set_font_name('Times New Roman')
		formats['reverse_dateformat'] = reverse_dateformat

		hourformat = workbook.add_format({'num_format':'hh:mm'})
		hourformat.set_align('center')
		hourformat.set_align('vcenter')
		hourformat.set_border(style=1)
		hourformat.set_font_size(10)
		hourformat.set_font_name('Times New Roman')
		formats['hourformat'] = hourformat

		return workbook, formats
