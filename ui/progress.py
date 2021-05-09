import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from component.dummyData import *
import time

# create
class on_progress(QWidget):
  # don't touch
  def __init__(self):
    super().__init__()
    self.init_ui()

  # code
  def init_ui(self):
  # 레이아웃
    layout = QGridLayout()
    self.setLayout(layout)

  # 학습 진행중 / 중단 알림
    self.indicator = QLabel('분산학습 준비 완료')
    self.indicator.setAlignment(Qt.AlignCenter)
    layout.addWidget(self.indicator, 0, 1)

  # 실시간 사용된 데이터와 크레딧
    self.used_data = QLabel('')
    self.used_credit = QLabel('')
    self.used_data.setAlignment(Qt.AlignCenter)
    self.used_credit.setAlignment(Qt.AlignCenter)
    layout.addWidget(self.used_data, 1, 0)
    layout.addWidget(self.used_credit, 1, 1)


    '''
      # 학습 진행중
        self.label = QLabel(self)
        self.label.setGeometry(QRect(25,25,200,200))
        self.label.setMinimumSize(QSize(100,100))
        self.label.setMaximumSize(QSize(100,100))
    
        self.loading = QMovie('./local_data/loading.gif', self)
        self.label.setMovie(self.loading)
        self.loading.start()
    '''

  # 학습 시작, 중단 및 결과 확인 버튼
    self.start_btn = QPushButton('학습 시작', self)  # bar button
    self.stop_btn = QPushButton('학습 중단', self)
    self.result_btn = QPushButton('결과 확인', self)
    self.result_btn.setEnabled(False)

  # 학습 현황 확인 / 2초마다 학습 현황 요청
    self.prgs_info = QLabel("현황 확인 중..")
    self.start_time = time.time() # 총 소요시간은 재기위한 타이머 / 학습 중단이 들어가면 스톱워치 기능 구현해야함
    self.timer = QTimer(self)  # 진행상태를 요청하기 위한 타이머
    self.timer.setInterval(2000)
    self.timer.timeout.connect(self.onProgressHandler)
    self.timer.start()
    layout.addWidget(self.prgs_info, 2, 2)
    self.prgs_info.setAlignment(Qt.AlignCenter)

  # 버튼 설정
    layout.addWidget(self.result_btn, 3, 1)
    layout.addWidget(self.start_btn, 3, 2)
    layout.addWidget(self.stop_btn, 3, 3)

  # 버튼 클릭시 메세지 출력
    self.start_btn.clicked.connect(self.onStartHandler)
    self.stop_btn.clicked.connect(self.onStopHandler)

  # 학습 요청
  def onStartHandler(self):

    self.indicator.setText('분산학습 진행중..')
    #res = project_start() / req.rest
    #self.loading.start()

  # 학습 현황 확인 / 2초 마다 트리거 됨
  def onProgressHandler(self):
    #res = project_progress() / req.rest
    #if (res["float"] == 1) onEndHandler()
    #else: print(res["message"])
    return

  #학습 중단
  def onStopHandler(self):
    self.indicator.setText('분산학습이 중단되었습니다.')
    #res = project_status() / req.rest
    #self.loading.stop()

  # 학습 완료 / 학습진행상태를 확인했을때 학습이 끝났으면 '결과확인'버튼을 활성화 함
  # def onEndHandler(self):
    #self.result_btn.setEnabled(True)

    #set_total_time(str(time.time() - self.start_time))