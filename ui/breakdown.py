from PyQt5.QtWidgets import *
from daig.api.rest import get_credit_log

class BrDownWidget(QWidget):
  def __init__(self):
    super().__init__()
    self.init_ui()

  def init_ui(self):
    self.formLayout = QFormLayout()
    self.formLayout.setSpacing(20)
    groupBox = QGroupBox()
    #groupBox.setStyleSheet()


    groupBox.setLayout(self.formLayout)
    scroll = QScrollArea()
    scroll.setWidget(groupBox)
    scroll.setWidgetResizable(True)
    scroll.setFixedHeight(400)
    scroll.setStyleSheet("QScrollBar:vertical {border: none;"
                         "background: white;"
                         "width: 5px;}"
                         )
    layout = QVBoxLayout(self)
    layout.addWidget(scroll)


  def call_credit_log(self):
    print('start')
    self.p_date = []
    row_len = self.formLayout.rowCount()
    for i in range(row_len):
      self.formLayout.removeRow(i)
    res = get_credit_log()
    self.creditLog_list = res["list"]


    for i in range(len(self.creditLog_list)):
      self.p_date.append(
        QLabel('  ' + self.creditLog_list[i]["details"] + '\t' +self.creditLog_list[i]["date"] + '\t' + str(self.creditLog_list[i]["amount"]) + '원'))
      self.formLayout.addRow(self.p_date[i])
      self.p_date[i].setStyleSheet('border: 1px solid #FFB914;'
                                   'font-size: 18px;'
                                   'font-family: 맑은 고딕;'
                                   'border-radius: 5px')
    pass

  # BrDownWidget이 트리거 될때마다 내역 불러오기
