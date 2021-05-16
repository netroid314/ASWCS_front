from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QThread, Qt
from component.constant import *
import time

from daig.api.main import *
from daig.api.rest import get_avaiable_project, start_learning, start_learning_internal, stop_learning_internal, is_project_finished

from daig.api.auth import get_auth_header, set_auth_header

class Worker(QThread):
  stop_learning = False

  def __init__(self, parent=None):
    super(Worker, self).__init__(parent)
    set_auth_header({'key':get_auth_header()})

  def run(self):
    self.stop_learning = False
    start_learning_internal()
    project_id = get_avaiable_project()
    if(project_id == -1): return
    result = start_learning(project_id)
    if((result == 'STOP') or (result == 'FAIL')):
      return
    time.sleep(2)
    if(not(self.stop_learning)):
      self.run()

  def stop(self):
    self.stop_learning = True
    stop_learning_internal()


class ProviderWidget(QWidget):
  # don't touch
  def __init__(self):
    super().__init__()
    self.init_ui()
    self.project_id = -1
    self.worker = Worker()

  # code
  def init_ui(self):
    self.pro_tab = QWidget()
    self.self_attend_p_id = '' # 자기가 참여한 p_id
    self.tabs = QTabWidget()
    self.tabs.addTab(self.pro_tab, 'Project')

    self.pro_tab.layout = QVBoxLayout()
    self.pro_table = QTableWidget()
    self.pro_table.setColumnCount(4)  # column 설정
    self.pro_table.setHorizontalHeaderLabels(['Project 이름(id)', 'task 개수', 'task 수행 평균 시간', 'credit'])

    project_header = self.pro_table.horizontalHeader()
    twidth = project_header.width()
    width = []
    for column in range(project_header.count()):
      project_header.setSectionResizeMode(column, QHeaderView.ResizeToContents)
      width.append(project_header.sectionSize(column))
    wfactor = twidth / sum(width)
    for column in range(project_header.count()):
      project_header.setSectionResizeMode(column, QHeaderView.Interactive)
      project_header.resizeSection(column, width[column] * wfactor)

    self.pro_tab.layout.addWidget(self.pro_table)
    self.pro_tab.setLayout(self.pro_tab.layout)

    self.train_start = QPushButton('학습 시작')
    self.train_stop = QPushButton('학습 중단')
    self.train_stop.setEnabled(False)
    self.train_start.clicked.connect(self.onTrainStartClicked)
    self.train_stop.clicked.connect(self.onTrainStopClicked)

    setButtonStyle(self.train_start)
    setButtonStyle(self.train_stop)

  # 사용자 페이지
    grid = QGridLayout()
    grid.addWidget(self.tabs, 0, 0, 1, 0)
    grid.addWidget(self.train_start, 1, 1)
    grid.addWidget(self.train_stop, 1, 2)

    self.setLayout(grid)

  # 요청자 레이아웃에서 참여를 누르면 실행되는 함수
  # 해당하는 프로젝트 아이디를 가져옴
  def onAttendHandler(self, p_id):
      print(p_id)
      #------- 여기에 p_id와 일치하는 프로젝트 요청 후 self.pro_table에 추가
      self.project_addItem(p_id)
      #------- 해당 프로젝트 분산학습 수행 요청
      self.train_start.setEnabled(False)
      self.train_stop.setEnabled(True)

    # 프로젝트 테이블 동적 생성
  def project_addItem(self, p_id, task_num='', task_pf_avrg='', credit=''):
    row = self.pro_table.rowCount()
    self.pro_table.insertRow(row)
    self.pro_table.setItem(row, 0, QTableWidgetItem(p_id))
    self.pro_table.setItem(row, 1, QTableWidgetItem(task_num))
    self.pro_table.setItem(row, 2, QTableWidgetItem(task_pf_avrg))
    self.pro_table.setItem(row, 3, QTableWidgetItem(credit))
    '''
    # json 형식의 res 데이터에 진행중인 프로젝트 정보가 여러개 올때 -> 받아오는 파라미터를 변경해줘야함
    for item in res:
      row = self.pro_table.rowCount()
      self.pro_table.setItem(row, 0, QTableWidgetItem(item['p_id']))
      self.pro_table.setItem(row, 1, QTableWidgetItem(item['task_num']))
      self.pro_table.setItem(row, 2, QTableWidgetItem(item['task_pf_avrg']))
      self.pro_table.setItem(row, 3, QTableWidgetItem(item['credit']))

    '''
    pass

    # 학습 시작 버튼을 눌렀을 경우
  def onTrainStartClicked(self):
      self.train_start.setEnabled(False)
      self.train_stop.setEnabled(True)
      self.repeat_learning()

      #현재 선택한(focus 되어 있는)프로젝트 p_id 받아옴
      #focused_p_id = self.pro_table.item(self.pro_table.currentRow(), 0).text()

    # 학습 중단 버튼을 눌렀을 경우
  def onTrainStopClicked(self):
      self.train_start.setEnabled(True)
      self.train_stop.setEnabled(False)
      self.worker.stop()

      #현재 선택한(focus 되어 있는)프로젝트 p_id 받아옴
      #focused_p_id = self.pro_table.item(self.pro_table.currentRow(), 0).text()

  def repeat_learning(self):
    self.project_id = get_avaiable_project()

    if(self.project_id == -1):
      self.worker.stop()
      return

    self.worker.setTerminationEnabled(True)
    self.worker.start()