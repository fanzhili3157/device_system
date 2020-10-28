from dingtalkchatbot.chatbot import DingtalkChatbot

ding_hook = "https://oapi.dingtalk.com/robot/send?access_token=29eda6fac064a8456914f8bf1c4a48330b55cb94d8a70588d99ad19c189d42c3"
game_ding = "https://oapi.dingtalk.com/robot/send?access_token=a56f145db2c7f95671d18de8e8e148e0ac598d14b419fd11baabe8f12bba4d9d"
players = {"fanzhili" : "15757115453",
                  "yinshuangfeng" : "",
                  "lipengfei" : "",
                  "caiyuping" : ""
                  }

class DingdingMes():
    def __init__(self,game_time):
        self.webhook = game_ding
        self.ding_robot = DingtalkChatbot(self.webhook)
        self.mes = "9人局预约："+game_time



    def send_text(self,mobiles=["15757115453"]):
        self.ding_robot.send_text(self.mes,at_mobiles=mobiles)

if __name__ == "__main__":

    game_time = "21:00"

    ding_mes = DingdingMes(game_time)
    ding_mes.send_text()
