from PyQt5.QtCore import QObject, pyqtSlot, QUrl, pyqtSignal
from PyQt5.QtPrintSupport import QPrintPreviewDialog
from PyQt5.QtWebKitWidgets import QWebView
from qutebrowser.widgets.tabbar import TabWidget
import logging

class TabbedBrowser(TabWidget):
    tabs = []
    cur_progress = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.currentChanged.connect(self.index_changed)
        self.tabopen("http://ddg.gg/")

    @pyqtSlot(str)
    def tabopen(self, url):
        tab = BrowserTab(self)
        tab.openurl(url)
        self.tabs.append(tab)
        self.addTab(tab, url)
        self.setCurrentWidget(tab)
        self.progress_changed(tab.progress)
        tab.loadProgress.connect(self.progress_changed)

    @pyqtSlot(str)
    def openurl(self, url):
        tab = self.tabs[self.currentIndex()]
        tab.openurl(url)

    @pyqtSlot()
    def close_act(self):
        if len(self.tabs) > 1:
            idx = self.currentIndex()
            self.tabs.pop(idx)
            self.removeTab(idx)
        else:
            # FIXME
            pass

    @pyqtSlot()
    def reload_act(self):
        self.currentWidget().reload()

    @pyqtSlot()
    def stop_act(self):
        self.currentWidget().stop()

    @pyqtSlot()
    def print_act(self):
        # FIXME that does not what I expect
        preview = QPrintPreviewDialog()
        preview.paintRequested.connect(self.currentWidget().print)
        preview.exec_()

    @pyqtSlot()
    def back_act(self):
        # FIXME display warning if beginning of history
        self.currentWidget().back()

    @pyqtSlot()
    def forward_act(self):
        # FIXME display warning if end of history
        self.currentWidget().forward()

    @pyqtSlot()
    @pyqtSlot(int)
    def scroll_down_act(self, count=50):
        self.currentWidget().page().mainFrame().scroll(0, count)

    @pyqtSlot()
    @pyqtSlot(int)
    def scroll_up_act(self, count=50):
        self.currentWidget().page().mainFrame().scroll(0, -count)

    @pyqtSlot()
    def switch_prev(self):
        idx = self.currentIndex()
        if idx > 0:
            self.setCurrentIndex(idx - 1)
        else:
            # FIXME
            pass

    @pyqtSlot()
    def switch_next(self):
        idx = self.currentIndex()
        if idx < self.count() - 1:
            self.setCurrentIndex(idx + 1)
        else:
            # FIXME
            pass

    @pyqtSlot(int)
    def progress_changed(self, prog):
        self.filter_signals(self.cur_progress, prog)

    def filter_signals(self, signal, *args):
        dbgstr = "{} ({})".format(
            signal.signal, ','.join([str(e) for e in args]))
        if self.currentWidget() == self.sender():
            logging.debug('{} - emitting'.format(dbgstr))
            signal.emit(*args)
        else:
            logging.debug('{} - ignoring'.format(dbgstr))

    @pyqtSlot(int)
    def index_changed(self, idx):
        tab = self.widget(idx)
        self.cur_progress.emit(tab.progress)

class BrowserTab(QWebView):
    parent = None
    progress = 0

    def __init__(self, parent):
        super().__init__(parent)
        self.loadProgress.connect(self.set_progress)
        self.show()

    def openurl(self, url):
        if not url.startswith('http://'):
            url = 'http://' + url
        super().load(QUrl(url))

    def set_progress(self, prog):
        self.progress = prog
