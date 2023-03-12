from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import numpy as np
import pandas as pd
import json


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def Send_mail_restaurants(Records,receiver_address):
    try:
        mail_content = '''Hello,
        This is a Automated mail. Please find all the top 10 restaurants below.
        '''
        #The mail addresses and password
        sender_address = 'rasa.upgrad.test@gmail.com'
        sender_pass = 'thisisnewpassword'
        
        mail_content=mail_content+"\n\n\n"
        mail_content=mail_content+("\n".join(Records))
        mail_content=mail_content+"\n \nThanks For the Support."
        #Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'Restaurant Listing from Zomato via Rasa'   #The subject line
        #The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pass) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        print('Mail Sent')
        return True
    except:
        return False

ZomatoData = pd.read_csv('zomato.csv')
ZomatoData = ZomatoData.drop_duplicates().reset_index(drop=True)
bins=[0,300,700, np.inf]
names=['Lesser than 300','Rs. 300 to 700','More than 700']
ZomatoData['BudgetRange']=pd.cut(ZomatoData['Average Cost for two'],bins, labels=names)
WeOperate = ['New Delhi', 'Gurgaon', 'Noida', 'Faridabad', 'Allahabad', 'Bhubaneshwar', 'Mangalore', 'Mumbai', 'Ranchi', 'Patna', 'Mysore', 'Aurangabad', 'Amritsar', 'Puducherry', 'Varanasi', 'Nagpur', 'Vadodara', 'Dehradun', 'Vizag', 'Agra', 'Ludhiana', 'Kanpur', 'Lucknow', 'Surat', 'Kochi', 'Indore', 'Ahmedabad', 'Coimbatore', 'Chennai', 'Guwahati', 'Jaipur', 'Hyderabad', 'Bangalore', 'Nashik', 'Pune', 'Kolkata', 'Bhopal', 'Goa', 'Chandigarh', 'Ghaziabad', 'Ooty', 'Gangtok', 'Shimla']
ZomatoData=ZomatoData.loc[ZomatoData['City'].isin(WeOperate)]


def RestaurantSearch(City,Cuisine,BudgetRange):
    print("City ->",City)
    print("Cuisine ->",Cuisine)
    print("BudgetRange ->",BudgetRange)
    if City.lower() in [x.lower() for x in WeOperate]:
        print("In IF")
        TEMP = ZomatoData[(ZomatoData['Cuisines'].apply(lambda x: Cuisine.lower() in x.lower())) & (ZomatoData['City'].apply(lambda x: City.lower() in x.lower())) & (ZomatoData['BudgetRange'].apply(lambda x:BudgetRange.lower() in x.lower()))].sort_values(by='Aggregate rating',ascending=False)   
        #TEMP = ZomatoData[(ZomatoData['Cuisines'].apply(lambda x: Cuisine.lower() in x.lower())) & (ZomatoData['City'].apply(lambda x: City.lower() in x.lower()))& (ZomatoData['BudgetRange'])]
        print(TEMP)
        return TEMP[['Restaurant Name','Address','Average Cost for two','Aggregate rating']]
    else:
        print("In Else")
        return False
        
        
class ActionSearchRestaurants(Action):
    def name(self):
        return 'action_search_restaurants'
    def run(self, dispatcher, tracker, domain):
        response=""
        follow_up="Is there anything else that I can help you with?"
        loc = tracker.get_slot('location')
        try:    
            if loc.lower() not in [x.lower() for x in WeOperate]:
                response= "Sorry!! We do not operate in that area yet"
                dispatcher.utter_message("-----"+response)
                dispatcher.utter_message(follow_up)
        except:
            pass
        cuisine =tracker.get_slot('cuisine')
        budget = tracker.get_slot('budget')
       
        print("loc ->",loc)
        print("Cuisine ->",cuisine)
        print("budget ->",budget)
        
        results = RestaurantSearch(City=loc,Cuisine=cuisine,BudgetRange=budget)
        
        print(results)
        Flag=0
        
        # try:
            # if results==False:
                # response= "Sorry!! We do not operate in that area yet"
                # dispatcher.utter_message("-----"+response)
                # dispatcher.utter_message(follow_up)
                                
                # Flag=1
        # except:
            # pass
        
        try:
            if (results.shape[0] == 0) and (Flag==0):
                response= "no results"
                dispatcher.utter_message("-----"+response)
                dispatcher.utter_message(follow_up)
                
        except:
            pass
        try:
            if (results.shape[0] != 0) and (Flag==0):
                response =" Showing you top rated restaurants: \n"
                for restaurant in results.iloc[:5].iterrows():
                    restaurant = restaurant[1]
                    response=response + F"Found {restaurant['Restaurant Name']} in {restaurant['Address']} has been rated {restaurant['Aggregate rating']} with avg cost for two as  {restaurant['Average Cost for two']} \n\n"
                dispatcher.utter_message("-----"+response)
        except:
            pass
        return [SlotSet('location',loc)]



class ActionSendMail(Action):
    def name(self):
        return 'action_send_mail'

    def run(self, dispatcher, tracker, domain):
        
        MailID = tracker.get_slot('mail_id')
        loc = tracker.get_slot('location')
        cuisine =tracker.get_slot('cuisine')
        budget = tracker.get_slot('budget')
        print("loc ->",loc)
        print("Cuisine ->",cuisine)
        print("budget ->",budget)
        dispatcher.utter_message("----- Mail Sent Successfully")
        results = RestaurantSearch(City=loc,Cuisine=cuisine,BudgetRange=budget)
        Restaurant=results.values.tolist()
        Res_list=[]
        for i in range(0,len(Restaurant)):
            temp=[str(i+1)]
            for word in Restaurant[i]:
                temp.append(str(word))
            
            Res_list.append("   ".join(temp))
        
        if len(Res_list) >10:
            Res_list=Res_list[:10]
        
        Send_mail_restaurants(Res_list,MailID)    
        return [SlotSet('mail_id',MailID)]
        