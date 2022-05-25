import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials


class Table:
    def __init__(self):
        self.CREDENTIALS_FILE = 'source/double-time-350509-496555a28790.json'
        self.credentials = ServiceAccountCredentials.\
            from_json_keyfile_name(self.CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                              'https://www.googleapis.com/auth/drive'])

        self.httpAuth = self.credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build('sheets', 'v4', http=self.httpAuth)

        self.spread_sheet_id = '1btHr0VqMh67SvqcRvbP6cXgn0Nib8xteeq_w5ub7PTY'

    def fill_questions(self, rows_cnt):
        for i in range(rows_cnt):
            self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spread_sheet_id, body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": "Лист номер один!{}2".format(next_sym('B', i)),
                    "values": [
                        ["Вопрос номер {}".format(i + 1)]
                    ]}
                ]
            }).execute()

    def add_user(self, user_name, index):
        self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spread_sheet_id, body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": "Лист номер один!A{}".format(index + 3),
                "values": [
                    ["{}".format(user_name)]
                ]}
            ]
        }).execute()

    def add_answer(self, answer, player_index, question_num):
        self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spread_sheet_id, body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": "Лист номер один!{}{}".format(next_sym('A', question_num - 1), player_index + 3),
                "values": [
                     ["{}".format(answer)]
                ]}
            ]
        }).execute()


def next_sym(sym, i):
    return chr(ord('B') + i)