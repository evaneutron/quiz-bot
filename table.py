# Подключаем библиотеки
import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = 'source/double-time-350509-496555a28790.json'  # Имя файла с закрытым ключом, вы должны подставить свое
# Читаем ключи из файла
credentials = ServiceAccountCredentials.\
    from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                              'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API

spread_sheet_id = '1btHr0VqMh67SvqcRvbP6cXgn0Nib8xteeq_w5ub7PTY'

"""driveService = apiclient.discovery.build('drive', 'v3', http = httpAuth) # Выбираем работу с Google Drive и 3 версию API
access = driveService.permissions().create(
    fileId = spread_sheet_id,
    body = {'type': 'user', 'role': 'writer', 'emailAddress': 'e.kuchendaeva@g.nsu.ru'},  # Открываем доступ на редактирование
    fields = 'id'
).execute()"""


def fill_questions(rows_cnt):
    for i in range(rows_cnt):
        results = service.spreadsheets().values().batchUpdate(spreadsheetId=spread_sheet_id, body={
            "valueInputOption": "USER_ENTERED",
            # Данные воспринимаются, как вводимые пользователем (считается значение формул)
            "data": [
                {"range": "Лист номер один!{}2".format(next_sym('B', i)),
                 "values": [
                     ["Вопрос номер {}".format(i + 1)]
                 ]}
            ]
        }).execute()
    return

def add_user(user_name, index):
    print(index)
    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spread_sheet_id, body={
        "valueInputOption": "USER_ENTERED",
        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
        "data": [
            {"range": "Лист номер один!A{}".format(index + 3),
             "values": [
                 ["{}".format(user_name)]
             ]}
        ]
    }).execute()

def add_answer(answer, player_index, question_num):
    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spread_sheet_id, body={
        "valueInputOption": "USER_ENTERED",
        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
        "data": [
            {"range": "Лист номер один!{}{}".format(next_sym('A', question_num - 1), player_index + 3),
             "values": [
                 ["{}".format(answer)]
             ]}
        ]
    }).execute()


def next_sym(sym, i):
    return chr(ord('B') + i)