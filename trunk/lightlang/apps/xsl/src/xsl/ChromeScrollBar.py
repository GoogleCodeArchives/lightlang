# -*- coding: utf8 -*-
#
# XSL - graphical interface for SL
# Copyright (C) 2007-2016 Devaev Maxim
#
# This file is part of XSL.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import Qt
import Config
import Const
import UserStyleCssCollection


#####
DefaultHighlightHeight = 5
MinCharacterDistance = 50


#####
class ChromeScrollBar(Qt.QScrollBar) :
	def __init__(self, parent = None) :
		Qt.QScrollBar.__init__(self, parent)

		self.setOrientation(Qt.Qt.Vertical)

		#####

		self._highlight_positions_list = []

		self._highlight_color = UserStyleCssCollection.highlightBackgroundColor()
		self._highlight_color.setAlpha(UserStyleCssCollection.highlightBackgroundOpacity())

		self._highlight_pen = Qt.QPen()
		self._highlight_pen.setColor(self._highlight_color)
		self._highlight_pen.setStyle(Qt.Qt.SolidLine)


	### Public ###

	def addHighlight(self, pos, count) :
		if len(self._highlight_positions_list) == 0 or abs(self._highlight_positions_list[-1]["pos"] - pos) > MinCharacterDistance :
			self._highlight_positions_list.append({ "pos" : pos, "count" : count })

	def drawHighlight(self) :
		self.update()

	def isHighlighted(self) :
		return bool(len(self._highlight_positions_list))

	def clearHighlight(self) :
		self._highlight_positions_list = []
		self.update()


	### Handlers ###

	def paintEvent(self, event) :
		Qt.QScrollBar.paintEvent(self, event)

		if len(self._highlight_positions_list) == 0 :
			return

		highlight_rects_list = []

		highlight_pass = self.style().pixelMetric(Qt.QStyle.PM_ScrollBarSliderMin) - 1
		highlight_area_height = self.height() - highlight_pass * 3

		for highlight_positions_list_item in self._highlight_positions_list :
			pos = highlight_area_height * highlight_positions_list_item["pos"] / highlight_positions_list_item["count"] + highlight_pass

			if len(highlight_rects_list) == 0 or pos > highlight_rects_list[-1].bottom() :
				highlight_rects_list.append(Qt.QRect(0, pos, self.width(), DefaultHighlightHeight))
			else :
				highlight_rects_list[-1].setHeight(highlight_rects_list[-1].height() + (DefaultHighlightHeight -
					highlight_rects_list[-1].bottom() + pos))

			if highlight_rects_list[-1].bottom() > highlight_area_height + highlight_pass :
				highlight_rects_list[-1].setHeight(highlight_rects_list[-1].height() - (highlight_rects_list[-1].bottom() -
					(highlight_area_height + highlight_pass)))

		painter = Qt.QPainter(self)
		painter.setPen(self._highlight_pen)
		painter.setBrush(self._highlight_color)
		for highlight_rects_list_item in highlight_rects_list :
			painter.drawRect(highlight_rects_list_item)
