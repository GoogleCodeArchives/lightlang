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


#####
Sl = Config.Prefix+"/bin/sl"
AllDictsDir = Config.Prefix+"/share/sl/dicts/"


#####
def tr(str) :
	return Qt.QApplication.translate("@default", str)


#####
class SlWordSearch(Qt.QObject) :
	def __init__(self, parent = None) :
		Qt.QObject.__init__(self, parent)

		#####

		self.proc = Qt.QProcess()
		self.proc.setReadChannelMode(Qt.QProcess.MergedChannels)
		self.proc.setReadChannel(Qt.QProcess.StandardOutput)

		self.proc_block_flag = False
		self.proc_kill_flag = False

		self.proc_args = Qt.QStringList()

		self.proc_output = Qt.QByteArray()

		self.dicts_list = Qt.QStringList()

		#####

		self.replaces_list = [
			["<em>This word is not found</em>", tr("<em>This word is not found</em>")],
			["<em>No dict is connected</em>", tr("<em>No dict is connected</em>")]
			]

		#####

		self.connect(self.proc, Qt.SIGNAL("error(QProcess::ProcessError)"), self.processError)
		self.connect(self.proc, Qt.SIGNAL("finished(int, QProcess::ExitStatus)"), self.processFinished)
		self.connect(self.proc, Qt.SIGNAL("stateChanged(QProcess::ProcessState)"), self.processStateChenged)
		self.connect(self.proc, Qt.SIGNAL("readyReadStandardOutput()"), self.setText)


	### Public ###

	def uFind(self, word) :
		self.find(word, "u")

	def cFind(self, word) :
		self.find(word, "c")

	def lFind(self, word) :
		self.find(word, "l")

	def iFind(self, word) :
		self.find(word, "i")

	def setDictsList(self, dicts_list) :
		self.dicts_list = dicts_list


	### Private ###

	def find(self, word, mode) :
		word = word.simplified()
		if word.isEmpty() :
			return
		word = word.toLower()

		if self.proc.state() == Qt.QProcess.Starting or self.proc.state() == Qt.QProcess.Running :
			self.setText()
			self.proc_kill_flag = True
			self.proc.kill()

		self.processStartedSignal()

		self.clearRequestSignal()

		self.proc_output.clear()

		self.proc_args.clear()
		self.proc_args << "--output-format=html" << "--use-list="+self.dicts_list.join("|") << "-"+mode << word

		while self.proc_block_flag :
			self.proc.waitForFinished()
		self.proc_kill_flag = False
		self.proc.start(Sl, self.proc_args)

	###

	def processError(self, error_code) :
		if error_code == Qt.QProcess.FailedToStart and not self.proc_kill_flag :
			Qt.QMessageBox.warning(None, Const.MyName,
				tr("An error occured when creating the search process"),
				Qt.QMessageBox.Yes)
		elif error_code == Qt.QProcess.Crashed and not self.proc_kill_flag :
			Qt.QMessageBox.warning(None, Const.MyName,
				tr("Error of the search process"),
				Qt.QMessageBox.Yes)
		elif error_code == Qt.QProcess.Timedout and not self.proc_kill_flag :
			Qt.QMessageBox.warning(None, Const.MyName,
				tr("Connection lost with search process"),
				Qt.QMessageBox.Yes)
		elif error_code == Qt.QProcess.WriteError and not self.proc_kill_flag :
			Qt.QMessageBox.warning(None, Const.MyName,
				tr("Error while writing data into the search process"),
				Qt.QMessageBox.Yes)
		elif error_code == Qt.QProcess.ReadError and not self.proc_kill_flag :
			Qt.QMessageBox.warning(None, Const.MyName,
				tr("Error while reading data from the search process"),
				Qt.QMessageBox.Yes)
		elif not self.proc_kill_flag :
			Qt.QMessageBox.warning(None, Const.MyName,
				tr("Unknown error occured while executing the search process"),
				Qt.QMessageBox.Yes)

	def processFinished(self, exit_code) :
		if exit_code and not self.proc_kill_flag :
			Qt.QMessageBox.warning(None, Const.MyName,
				tr("Error of the search process"),
				Qt.QMessageBox.Yes)
		self.processFinishedSignal()

	def processStateChenged(self, state) :
		self.proc_block_flag = ( True if state == Qt.QProcess.Starting or state == Qt.QProcess.Running else False )

	def setText(self) :
		self.proc_output.append(self.proc.readAllStandardOutput())

		text = Qt.QString.fromLocal8Bit(str(self.proc_output))
		#for replaces_list_item in self.replaces_list :
		#	text.replace(replaces_list_item[0], replaces_list_item[1])

		self.textChangedSignal(text)


	### Signals ###

	def processStartedSignal(self) :
		self.emit(Qt.SIGNAL("processStarted()"))

	def processFinishedSignal(self) :
		self.emit(Qt.SIGNAL("processFinished()"))

	def clearRequestSignal(self) :
		self.emit(Qt.SIGNAL("clearRequest()"))

	def textChangedSignal(self, text) :
		self.emit(Qt.SIGNAL("textChanged(const QString &)"), text)
