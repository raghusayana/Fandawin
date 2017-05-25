#! /usr/bin/python
import requests
import json
import unicodedata
import sys
import operator
from collections import Counter
import os
from datetime import datetime
import shutil
import glob

def createtable(data,daywin,time):
  f = open('/home/user/data/currentdata.table', 'w')
  f.write("<table border=\"1\">")
  f.write("<tr> "+time+ "</tr>")
  for dat in data:
    f.write("<tr>")
    f.write("<td> "+ str(dat[0])+" </td> <td> "+str(dat[1])+" </td> <td> "+str(daywin[dat[0]])+" </td>")
    f.write("</tr>")
  f.write("</table>")
  f.write("</br>")
  f.close()

payload = {"user_id":"userid","password":"password"}
authenticate_URL = 'https://wz4j065jwc.execute-api.ap-southeast-1.amazonaws.com/production/users/authenticate'
league_URL = 'https://wz4j065jwc.execute-api.ap-southeast-1.amazonaws.com/production/users/leaguemembers?leagueId=leagueid'

headers = {'content-type': 'application/json'}

authenticate_response = requests.post(authenticate_URL, data=json.dumps(payload), headers=headers)
con_dict = dict()

if authenticate_response.status_code == 200:
  authenticate_reponse_text=authenticate_response.text
  decode_response=unicodedata.normalize('NFKD', authenticate_reponse_text).encode('ascii','ignore')
  access_token = json.loads(decode_response)['data']['access_token']

  headers_league = {'content-type': 'application/json','accesstoken':access_token,'userid':'userid'}
  data_response=requests.get(league_URL,headers=headers_league)

  if data_response.status_code == 200:
    decode_data_response=unicodedata.normalize('NFKD', data_response.text).encode('ascii','ignore')
    final_results = json.loads(decode_data_response)['data']['leagueMembers']

    for item in final_results:
      con_dict[str(item["teamName"])] = item["totalPoints"]
      #print(item["totalPoints"],str(item["teamName"]),item["rank"])

  #print(json.dumps(con_dict, ensure_ascii=True))
else:
  print("Authentication Failed !!!")
  sys.exit(1)

with open('/home/user/data/previous_results.json') as previous_data_file:
    previous_data = json.load(previous_data_file)

day_winner = dict()
for name, points in con_dict.items():
  day_winner[name] = (points - previous_data[name])
  #print(name,(points - previous_data[name]))

count = Counter(day_winner.values())
#print(count[0])
i = datetime.now()
file_name_conv = i.strftime('%Y_%m_%d_%H_%M_%S')
if count[0] < 5:
  os.rename('/home/user/data/previous_results.json', "/home/user/data/previous_results.json_"+file_name_conv)
  os.rename('/home/user/data/currentdata.table', "/home/user/data/currentdata.table_"+file_name_conv)
  with open('/home/user/data/previous_results.json', 'w') as outfile:
    json.dump(con_dict, outfile,ensure_ascii=False)

  sorted_day_winner = sorted(day_winner.items(), key=operator.itemgetter(1), reverse=True)
  #print(sorted_day_winner)
  createtable(sorted_day_winner,con_dict,file_name_conv)

  outfilename = '/var/www/html/fandawin'
  with open(outfilename, 'wb') as outfile:
    outfile.write("<html>")
    for filename in sorted(glob.glob('/home/user/data/*.table*')):
        if filename == outfilename:
            # don't want to copy the output into the output
            continue
        with open(filename, 'rb') as readfile:
            shutil.copyfileobj(readfile, outfile)
    outfile.write("</html>")
    outfile.close()
  print("Completed execution successfully - created page at "+file_name_conv)

print("Completed execution successfully - End of Script at "+file_name_conv)
