from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
import csv

#input slack token and signing_secret
SLACK_TOKEN = ''
SLACK_SIGNING_SECRET = ''
app = Flask(__name__)

pre_request_user_list = []

# /listening 으로 슬랙 이벤트를 받습니다.
slack_events_adaptor = SlackEventAdapter(SLACK_SIGNING_SECRET, "/listening", app)
slack_web_client = WebClient(token=SLACK_TOKEN)

filename_list_cubest_easy = 'easy5_list.csv'
filename_list_cubest_jeasy = 'jeasy5_list.csv'
filename_list_cubest_snack = 'snack5_list.csv'
filename_list_cubest_ice = 'ice5_list.csv'
filename_list_cubest_food = 'food5_list.csv'
filename_list_cubest_drink = 'drink5_list.csv'
filename_list_pbgoods = 'favor_pb_goods_list.csv'
filename_list_plus_event = 'plus_event_list.csv'

def get_text_from_file(filename):
    with open('C:/Users/student/Desktop/CU/'+filename) as file:
        reader = csv.reader(file, delimiter='|')
        list_=[]
        for row in reader:
            title = row[1]
            price = row[2]
            list_.append(title + ':' + price + '원')
        return '\n'.join(list_)

def get_list_from_file(filename):
    list_ = []
    with open('C:/Users/student/Desktop/CU/'+filename,'r',encoding='UTF-8') as file:
        reader = csv.reader(file, delimiter='|',quotechar='"')
        for row in reader:
            if row:
                list_.append([row[0],row[1],row[2]])
    return list_
@slack_events_adaptor.on("app_mention")
def app_mentioneevent_datad(event_data):
   channel = event_data["event"]["channel"]
   text = event_data["event"]["text"]
   user = event_data["event"]["user"]
   event_ts = event_data["event"]["ts"]
   unique_user = {'channel':channel,
                  'user': user,
                  'event_ts': float(event_ts),
                  'request':'NONE'}
   keywords = ""
    #2분 넘어가면 지워지게 처리하는 로직
   for pre_request_user in range(len(pre_request_user_list)):
       if float(event_ts) - float(pre_request_user_list[pre_request_user]["event_ts"]) >= 120:
            del pre_request_user_list[pre_request_user]
    # 최근 기록에 있는지 확인하는 로직
   pre_request_user = list(filter(lambda a:a['channel']==channel and a['user']==user, pre_request_user_list))
   #분기처리 > 텍스트 처리
   if len(pre_request_user) > 0 :
        now_dic = pre_request_user[0]
        text_after = text[text.index('>')+1:].strip()
        if now_dic["request"].startswith("CUBEST") :
            list_in_CUBEST = ["간편식사","즉석조리","과자류","아이스크림","식품","음료"]
            if text_after in list_in_CUBEST:
                if text_after == "간편식사":
                    keywords = "간편식사 베스트 5:\n"
                    list_cubest_easyeat = get_text_from_file(filename_list_cubest_easy)
                    keywords += list_cubest_easyeat
                    now_dic["request"] = "NONE"
                elif text_after == "즉석조리":
                    keywords = "즉석조리 베스트 5:\n"
                    list_cubest_instant = get_text_from_file(filename_list_cubest_jeasy)
                    keywords += list_cubest_instant
                    now_dic["request"] = "NONE"
                elif text_after == "과자류":
                    keywords = "과자류 베스트 5:\n"
                    list_cubest_snack = get_text_from_file(filename_list_cubest_snack)
                    keywords += list_cubest_snack
                    now_dic["request"] = "NONE"
                elif text_after == "아이스크림":
                    keywords = "아이스크림 베스트 5:\n"
                    list_cubest_icecream = get_text_from_file(filename_list_cubest_ice)
                    keywords += list_cubest_icecream
                    now_dic["request"] = "NONE"
                elif text_after == "식품":
                    keywords = "식품 베스트 5:\n"
                    list_cubest_food = get_text_from_file(filename_list_cubest_food)
                    keywords += list_cubest_food
                    now_dic["request"] = "NONE"
                elif text_after == "음료":
                    keywords = "음료 베스트 5:\n"
                    list_cubest_drink = get_text_from_file(filename_list_cubest_drink)
                    keywords += list_cubest_drink
                    now_dic["request"] = "NONE"
            else:
                keywords = '["간편식사"/"즉석조리"/"과자류"/"아이스크림"/"식품"/"음료"] 카테고리를 입력해 CU의 베스트상품을 확인하세요!'
        elif now_dic["request"].startswith("PLUS"):
            if now_dic["request"] == "PLUS":
                list_in_PLUS = ["1+1","2+1","3+1"]
                if text_after == list_in_PLUS[0]:
                    keywords = '"1+1"를 입력했습니다! [리스트/검색:원하는검색명]을 통해 1+1제품을 확인하세요!'
                    now_dic["request"] += "BUYONE"
                elif text_after == list_in_PLUS[1]:
                    keywords = '"2+1"를 입력했습니다! [리스트/검색:원하는검색명]을 통해 2+1제품을 확인하세요!'
                    now_dic["request"] += "BUYTWO"
                elif text_after == list_in_PLUS[2]:
                    keywords = '"3+1"를 입력했습니다! [리스트/검색:원하는검색명]을 통해 3+1제품을 확인하세요!'
                    now_dic["request"] += "BUYTHREE"
                else:
                    keywords = '["1+1"/"2+1"/"3+1"]로 원하는 플러스 상품을 확인하세요!'
                print()
            elif "BUYONE" in now_dic["request"]:
                if "검색" in text_after:
                    search_keyword = text_after.split(':')[1]
                    keywords = "1+1상품 검색 결과입니다."
                    list_buyone_list = get_list_from_file(filename_list_plus_event)
                    list_buyone_search_list = [(n[0] + ":" + n[1] + "원") for n in list_buyone_list if '1+1' == n[2] and search_keyword in n[0]]
                    list_buyone_search_text = '\n' + '\n'.join(list_buyone_search_list)
                    keywords += list_buyone_search_text
                    now_dic["request"] = "NONE"
                elif text_after in "리스트":
                    keywords = "1+1 상품 리스트 결과입니다."
                    list_buyone_list = get_list_from_file(filename_list_plus_event)
                    list_buyone_list_list = [(n[0] + ":" + n[1] + "원") for n in list_buyone_list if '1+1' == n[2]]
                    list_buyone_list_text = '\n' + '\n'.join(list_buyone_list_list)
                    keywords += list_buyone_list_text
                    now_dic["request"] = "NONE"
                else:
                    keywords = '"리스트" / "검색:원하는검색명"로 1+1상품을 확인하세요!'
            elif "BUYTWO" in now_dic["request"]:
                if "검색" in text_after:
                    search_keyword = text_after.split(':')[1]
                    keywords = "2+1상품 검색 결과입니다."
                    list_buytwo_list = get_list_from_file(filename_list_plus_event)
                    list_buytwo_search_list = [(n[0] + ":" + n[1] + "원") for n in list_buytwo_list if '2+1' == n[2] and search_keyword in n[0]]
                    list_buytwo_search_text = '\n' + '\n'.join(list_buytwo_search_list)
                    keywords += list_buytwo_search_text
                    now_dic["request"] = "NONE"
                elif text_after in "리스트":
                    keywords = "2+1 상품 리스트 결과입니다."
                    list_buytwo_list = get_list_from_file(filename_list_plus_event)
                    list_buytwo_list_list = [(n[0] + ":" + n[1] + "원") for n in list_buytwo_list if '2+1' == n[2]]
                    list_buytwo_list_text = '\n' + '\n'.join(list_buytwo_list_list)
                    keywords += list_buytwo_list_text
                    now_dic["request"] = "NONE"
                else:
                    keywords = '"리스트" / "검색:원하는검색명"로 2+1상품을 확인하세요!'
            elif "BUYTHREE" in now_dic["request"]:
                if "검색" in text_after:
                    search_keyword = text_after.split(':')[1]
                    keywords = "3+1상품 검색 결과입니다."
                    list_buythree_list = get_list_from_file(filename_list_plus_event)
                    list_buythree_search_list = [(n[0] + ":" + n[1] + "원") for n in list_buythree_list if '3+1' == n[2] and search_keyword in n[0]]
                    list_buythree_search_text = '\n' + '\n'.join(list_buythree_search_list)
                    keywords += list_buythree_search_text
                    now_dic["request"] = "NONE"
                elif text_after in "리스트":
                    keywords = "3+1 상품 리스트 결과입니다."
                    list_buythree_list = get_list_from_file(filename_list_plus_event)
                    list_buythree_list_list = [(n[0] + ":" + n[1] + "원") for n in list_buythree_list if '3+1' == n[2]]
                    list_buythree_list_text = '\n' + '\n'.join(list_buythree_list_list)
                    keywords += list_buythree_list_text
                    now_dic["request"] = "NONE"
                else:
                    keywords = '"리스트" / "검색:원하는검색명"로 3+1상품을 확인하세요!'
        elif now_dic["request"].startswith("PBGOODS"):
            if "검색" in text_after:
                search_keyword = text_after.split(':')[1]
                keywords = "PB상품 검색 결과입니다."
                list_pbgoods_search = get_list_from_file(filename_list_pbgoods)
                list_pbgoods_search_pb = [(n[1] + ":" + n[2] + "원") for n in list_pbgoods_search if 'PB_PB' == n[0] and search_keyword in n[1]]
                list_pbgoods_search_diff = [(n[1] + ":" + n[2] + "원") for n in list_pbgoods_search if 'PB_diff' == n[0] and search_keyword in n[1]]
                list_pbgoods_search = '\n' + '\n'.join(list_pbgoods_search_pb) + '\n' + '\n'.join(list_pbgoods_search_diff)
                keywords += list_pbgoods_search
                now_dic["request"] = "NONE"
            elif text_after in "인기":
                keywords = "PB상품 인기 BEST 결과입니다."
                list_pbgoods_best = get_list_from_file(filename_list_pbgoods)
                list_pbgoods_best_pb = [(n[1]+":"+n[2]+"원") for n in list_pbgoods_best if 'PB_PB'==n[0]][:5]
                list_pbgoods_best_diff = [(n[1]+":"+n[2]+"원") for n in list_pbgoods_best if 'PB_diff'==n[0]][:5]
                list_pbgoods_best = '\n'+'\n'.join(list_pbgoods_best_pb)+'\n'+'\n'.join(list_pbgoods_best_diff)
                keywords += list_pbgoods_best
                now_dic["request"] = "NONE"
            else:
                keywords = '"인기" / "검색:원하는검색명"로 PB상품을 확인하세요!'
        else:
            list_in_NONE = ["CU베스트","플러스행사","PB상품"]
            if text_after in list_in_NONE:
                if text_after == list_in_NONE[0]:
                    keywords = '"CU베스트"를 입력했습니다! 카테고리를 골라주세요 [간편식사/즉석조리/과자류/아이스크림/식품/음료]'
                    now_dic["request"] = "CUBEST"
                elif text_after == list_in_NONE[1]:
                    keywords = '"플러스행사"를 입력했습니다! 카테고리를 골라주세요 [1+1/2+1/3+1]'
                    now_dic["request"] = "PLUS"
                elif text_after == list_in_NONE[2]:
                    keywords = '"PB상품"를 입력했습니다! 카테고리를 골라주세요 [인기 / 검색:원하는검색명]'
                    now_dic["request"] = "PBGOODS"
            else:
                keywords = '"CU베스트 / 플러스행사 / PB상품"을 입력해주세요!'
        now_dic["event_ts"] = float(event_ts)
   else:
        # 처음 오신분들 / 아직 처음도 안물어본 사람들
        keywords = '안녕하세요 cu입니다!("CU베스트 / 플러스행사 / PB상품"을 입력해주세요!)'
        pre_request_user_list.append(unique_user)
   slack_web_client.chat_postMessage(
       channel=channel,
       text=keywords
   )
if __name__ == '__main__':
   app.run('127.0.0.1', port=4040)
