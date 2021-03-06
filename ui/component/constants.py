num_of_prgs = 0

def setLoginButtonStyle(lg):
    lg.setStyleSheet('color: white;'
                     'background-color: rgb(251, 86, 7);'
                     'border-radius: 20px;')

def setButtonStyle(bt):
    bt.setFixedSize(110, 30)
    bt.setStyleSheet("QPushButton"
                     "{"
                     'color: rgb(251, 86, 7);'
                     'background-color: white;'
                     'border: 1px solid rgb(251, 86, 7);'
                     'border-radius: 5px;'
                     "}"
                     "QPushButton::pressed"
                     "{"
                     'color: rgb(251, 86, 7);'
                     'background-color: white;'
                     'border: 1px solid rgb(123, 207, 146);'
                     'border-radius: 5px;'
                     "}"
                     "QPushButton::disabled"
                     "{"
                     'color: gray;'
                     'background-color: white;'
                     'border: gray;'
                     'border-radius: 5px;'
                     "}"
                     )

def setBigButtonStyle(bt):
    bt.setFixedSize(120, 40)
    bt.setStyleSheet("QPushButton"
                     "{"
                     'color: black;'
                     'font-weight: bold;'
                     'background-color: #FFB914;'
                     'border: 2px solid #FFB914;'
                     'border-radius: 18px;'
                     "}"
                     "QPushButton::pressed"
                     "{"
                     'color: black;'
                     'font-weight: bold;'
                     'background-color: #9C7314;'
                     'border: 2px solid #9C7314;'
                     'border-radius: 18px;'
                     "}"
                     )

def setLabelStyle(lb):
    lb.setStyleSheet('color: rgb(251, 86, 7)')

# 엔터 눌렀을 때의 동작
def enterPressedHandler(edit, action):
    edit.returnPressed.connect(action)

# lineEdit 기본설정
def setEditStandard(edit ,x_val, y_val, place_holder):
    if(x_val > 0): edit.move(x_val, y_val)
    edit.setPlaceholderText(place_holder)
    edit.setStyleSheet('border: 1px solid gray;'
                       'border-radius: 5px')

# 크레딧 잔액 가져오기
def getUserCreditAmount():
    pass

# 크레딧 잔액 요청
def setUserCreditAmount(user_key):
    pass
    #----- 잔액 요청
    #return 잔액