import sys
import os
import tensorflow as tf
from daig.api.rest import *
from PyQt5.QtWidgets import QLineEdit, QWidget, QLabel, QPushButton, QComboBox, QGridLayout, QFileDialog, QProgressBar, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from daig.requester import project
from component.constants import setLabelStyle, setButtonStyle, setEditStandard
import numpy as np
import math
import requests
from tempfile import TemporaryFile
from daig.api.auth import get_auth_header

class UploadThread(QThread):
  stop_learning = False
  pbar_signal=pyqtSignal(dict)

  def __init__(self,auth, parent=None):
    super(UploadThread, self).__init__(parent)
    self.auth=auth
    print(auth)
    self.model_path=parent.model_path.text()
    self.train_lbl_path=parent.train_lbl_path.text()
    self.train_img_path=parent.train_img_path.text()
    self.task_num = int(parent.cho_task.text())
    self.step_num = int(parent.cho_step.text())
    self.epoch = int(parent.cho_epoch.text())
    self.batch_size = int(parent.cho_batch.text())
    self.contributor = int(parent.cho_contributor.text())
    self.valid_rate = float(parent.cho_valid.text())

  def run(self):
    model = tf.keras.models.load_model(self.model_path)

    total_parameters = 0
    for variable in tf.trainable_variables():
        shape = variable.get_shape()
        variable_parameters = 1
        for dim in shape:
            variable_parameters *= dim.value
        total_parameters += variable_parameters


    res = self.create_project(model.get_weights(), data = {
        'total_task' : self.task_num,
        'step_size' : self.step_num,
        'epoch': self.epoch,
        'batch_size': self.batch_size,
        'valid_rate': self.valid_rate,
        'parameter_number': total_parameters,
        'max_contributor': self.contributor
    })

    project.uid=res["project_uid"]

    self.upload_model(self.model_path,project.uid)
    self.upload_data(self.train_img_path,self.train_lbl_path,project.uid,self.task_num)
    

  def create_project(self,initial_weight,data=None):
    with TemporaryFile() as tf:
      np.save(tf, np.array(initial_weight,dtype=object))
      _ = tf.seek(0)
      res = requests.post(f'{base_url}/project/create/', files={'weight':tf},data=data, headers={'AUTH':self.auth})

    return res.json()

  def upload_model(self, model_path, project_uid):
    res=requests.post(f'{base_url}/project/model/upload',data={ # ????????? url ??????
      'project_uid':project_uid,
      'model':'model.h5'
    }, headers={'AUTH':self.auth})
    print(res.json())

    url=res.json()['model_url'] # presigned url

    with open(model_path, 'rb') as f:
      requests.put(url=url,data=f) # ????????? ?????????
        
    print('model successfully uploaded')

  def upload_each_data(self,data, label, project_uid, idx):
    res=requests.post(f'{base_url}/project/data/upload',data={ # ????????? url ??????
      'project_uid':project_uid,
      'data': f'train_data_{idx}',
      'label': f'train_label_{idx}',
      'index': idx
    }, headers={'AUTH':self.auth})

    url=res.json()['label_url'] # presigned url
    with TemporaryFile() as tf:
      np.save(tf, label)
      _ = tf.seek(0)
      requests.put(url=url,data=tf) # ?????? ?????????

    url=res.json()['data_url'] # presigned url
    with TemporaryFile() as tf:
      np.save(tf, data)
      _ = tf.seek(0)
      requests.put(url=url,data=tf) # ????????? ?????????

  def upload_data(self,data_path,label_path,project_uid,task_num):
    data=np.load(data_path, allow_pickle=True)
    label=np.load(label_path, allow_pickle=True)
    data_split=np.split(data,task_num)
    label_split=np.split(label,task_num)

    pbar_rate=0
    r=math.floor(10000/task_num)*0.01
    for idx in range(task_num):
      self.upload_each_data(data_split[idx], label_split[idx], project_uid, idx)
      pbar_rate+=r
      self.pbar_signal.emit({
        "is_completed":False,
        "num":pbar_rate
      })
      print(f'{idx} uploaded')
    self.pbar_signal.emit({
      "is_completed":True,
      "num":100
    })
    print('data uploading finished')


class DataUploadWidget(QWidget):
  # don't touch
  def __init__(self):
    super().__init__()
    self.init_ui()

  # code
  def init_ui(self):

    # ?????? ?????? ??????
    self.model = QLabel('model')
    self.train_img = QLabel('train image')
    self.train_lbl = QLabel('train label')
    #self.valid_img = QLabel('valid image')
    #self.valid_lbl = QLabel('valid label')
    self.p_contributer = QLabel('max contributer : ')
    self.p_task_div = QLabel('Task ?????? ??????')
    self.p_step_task = QLabel('Step??? task ??????')
    self.p_epoch = QLabel('Epoch number')
    self.p_batch = QLabel('Batch size')
    self.p_contributor = QLabel('?????? ????????????')
    self.p_valid = QLabel('?????? ??????')
    self.model_path = QLabel('')
    self.model_path.setMinimumSize(250, 20)
    self.train_img_path = QLabel('')
    self.train_lbl_path = QLabel('')
    #self.valid_img_path = QLabel('')
    #self.valid_lbl_path = QLabel('')

    setLabelStyle(self.model)
    setLabelStyle(self.train_img)
    setLabelStyle(self.train_lbl)
    setLabelStyle(self.p_task_div)
    setLabelStyle(self.p_step_task)
    setLabelStyle(self.p_epoch)
    setLabelStyle(self.p_batch)
    setLabelStyle(self.p_contributor)
    setLabelStyle(self.p_valid)

  # ?????? ????????? ??????
    self.model_btn = QPushButton('?????????')
    self.model_btn.clicked.connect(self.model_btn_clicked)
    self.train_img_btn = QPushButton('?????????')
    self.train_img_btn.clicked.connect(self.train_img_btn_clicked)
    self.train_lbl_btn = QPushButton('?????????')
    self.train_lbl_btn.clicked.connect(self.train_lbl_btn_clicked)
    #self.valid_img_btn = QPushButton('?????????')
    #self.valid_img_btn.clicked.connect(self.train_img_btn_clicked)
    #self.valid_img_btn = QPushButton('?????????')
    #self.valid_img_btn.clicked.connect(self.train_lbl_btn_cliked)

    setButtonStyle(self.model_btn)
    setButtonStyle(self.train_img_btn)
    setButtonStyle(self.train_lbl_btn)

 # task ?????? ?????? ??????
    self.cho_task = QLineEdit(self)
    setEditStandard(self.cho_task, 0, 0, 'task num')

  # step??? task ??????
    self.cho_step = QLineEdit(self)
    setEditStandard(self.cho_step, 0, 0, 'step num')

  # epoch ??????
    self.cho_epoch = QLineEdit(self)
    setEditStandard(self.cho_epoch, 0, 0, 'epoch')

  # mini batch ??????
    self.cho_batch = QLineEdit(self)
    setEditStandard(self.cho_batch, 0, 0, 'batch size')

  # ???????????? ??????
    self.cho_contributor = QLineEdit(self)
    setEditStandard(self.cho_contributor, 0, 0, 'max contributor')

  # ?????? ????????? ??????
    self.cho_valid = QLineEdit(self)
    setEditStandard(self.cho_valid, 0, 0, 'validation split')

  # ?????? ?????? ??????
    self.train_start = QPushButton('???????????? ??????')
    self.train_start.clicked.connect(self.train_start_clicked)
    setButtonStyle(self.train_start)

    # progress bar
    self.pbar=QProgressBar()

    # ???????????? ?????? ??? ??????
    layout = QGridLayout()
    layout.addWidget(self.model, 0, 0)
    layout.addWidget(self.model_path, 0, 1)
    layout.addWidget(self.model_btn, 0, 2)
    layout.addWidget(self.train_img, 1, 0)
    layout.addWidget(self.train_img_path, 1, 1)
    layout.addWidget(self.train_img_btn, 1, 2)
    layout.addWidget(self.train_lbl, 2, 0)
    layout.addWidget(self.train_lbl_path, 2, 1)
    layout.addWidget(self.train_lbl_btn, 2, 2)
    layout.addWidget(self.p_task_div, 3, 0)
    layout.addWidget(self.cho_task, 3, 2)
    layout.addWidget(self.p_step_task, 4, 0)
    layout.addWidget(self.cho_step, 4, 2)
    layout.addWidget(self.p_epoch, 5, 0)
    layout.addWidget(self.cho_epoch, 5, 2)
    layout.addWidget(self.p_batch, 6, 0)
    layout.addWidget(self.cho_batch, 6, 2)
    layout.addWidget(self.p_contributor, 7, 0)
    layout.addWidget(self.cho_contributor, 7, 2)
    layout.addWidget(self.p_valid, 8, 0)
    layout.addWidget(self.cho_valid, 8, 2)
    
    layout.addWidget(self.train_start, 9, 2)
    layout.addWidget(self.pbar, 9, 0, 1, 2)

    self.setLayout(layout)

  # task ?????? ?????? ??????
  def onChanged(self, text):
    self.cho_task.setText(text)
    self.id.adjustSize()
    self.cho_step.setText(text)
    self.pwd.adjustSize()

  # ?????? ?????? ???????????? / ????????? ??????????????? ???????????????. Tensorflow Model Format ??????
  def model_btn_clicked(self):
    self.m_file = QFileDialog.getOpenFileName(self, './', filter="*.h5")
    self.model_path.setText(self.m_file[0])

  # train img ?????? ????????????
  def train_img_btn_clicked(self):
    self.train_img_file = QFileDialog.getOpenFileName(
        self, './', filter="*.npy")
    self.train_img_path.setText(self.train_img_file[0])

    #self.train_img_path.text() : ????????? ?????? ????????? ??????
  # train lbl ?????? ????????????
  def train_lbl_btn_clicked(self):
    self.train_lbl_file = QFileDialog.getOpenFileName(
        self, './', filter="*.npy")
    self.train_lbl_path.setText(self.train_lbl_file[0])


  '''
  def valid_img_btn_clicked(self):
    self.valid_img_file = QFileDialog.getOpenFileName(self, filter="*.npy")
    self.valid_img_path.setText(self.train_img_file[0])

  def valid_lbl_btn_clicked(self):
    self.valid_lbl_file = QFileDialog.getOpenFileName(self, filter="*.npy")
    self.valid_lbl_path.setText(self.train_lbl_path[0])
  '''

  def train_start_clicked(self):
    format_check = self.input_format_check()
    if(format_check):
      QMessageBox.about(self, 'DAIG', format_check)

    self.train_start.setEnabled(False)
    self.upload_thread=UploadThread(get_auth_header(),self)
    self.upload_thread.pbar_signal.connect(self.update_pbar)

    self.upload_thread.start()
    return

  @pyqtSlot(dict)
  def update_pbar(self, content):
    is_completed=content["is_completed"]
    value=content["num"]
    self.pbar.setValue(value)
    if is_completed:
      self.complete_upload()

  def complete_upload(self):
    raise NotImplementedError

  def input_format_check(self):
    if((int(self.cho_task.text()) != float(self.cho_task.text()))):
      return "??? task ????????? ??????????????? ??????????????????"
    if((int(self.cho_step.text()) != float(self.cho_step.text()))):
      return "step??? ????????? ??????????????? ??????????????????"
    if((int(self.cho_epoch.text()) != float(self.cho_epoch.text()))):
      return "epoch ?????? ??????????????? ??????????????????"
    if((int(self.cho_batch.text()) != float(self.cho_batch.text()))):
      return "batch size??? ??????????????? ??????????????????"
    if((int(self.cho_contributor.text()) != float(self.cho_contributor.text()))):
      return "????????? ?????? ??????????????? ??????????????????"
    if(float(self.cho_valid.text()) >= 1 or float(self.cho_valid.text()) < 0):
      return "validation split??? 0?????? 1????????? ???????????? ?????????."
    if(int(self.cho_task.text()) < 10 or int(self.cho_task.text()) > 100):
      return "task??? ????????? ?????? ????????? ????????????."
    if(int(self.cho_step.text()) < 1 or int(self.cho_step.text()) > 20):
      return "step??? ????????? ?????? ????????? ????????????."
    if(int(self.cho_contributor.text()) < 1):
      return "?????? ????????? ?????? ?????? ???????????? ?????????."
    if(int(self.cho_contributor.text()) > int(self.cho_step.text())):
      return "?????? ????????? ?????? step size??? ?????? ??? ????????????."
    if(int(self.cho_task.text()) % int(self.cho_step.text()) != 0):
      return "??? Task ????????? step size??? ????????? ????????? ??? ????????? ?????????."

    return False