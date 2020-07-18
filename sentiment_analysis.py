

import pandas as pd
from textblob import TextBlob
import csv


#this function creates 2 csv files which are used for plotting on the dashboard
def plot_overall_sent(data_frame,file_writer):
    #weight function applied on each tweet in the dataframe
    data_frame["wgt"]=data_frame.apply(lambda row:(row["Retweet_Count"]*0.3+row["Actual Tweet"]["favorite_count"]*0.1)*row["sentiment_subjectivity"],axis=1)

    avg_sentiment=0
    wgt_sum = 0
    positive = 0
    w_positive = 0
    s_positive = 0
    negative = 0
    w_negative = 0
    s_negative = 0
    neutral = 0
    for i in data_frame.index:
        tweet_sentiment=data_frame["wgt"][i]*data_frame["sentiment_polarity"][i]
        avg_sentiment+=tweet_sentiment
        wgt_sum+=data_frame["wgt"][i]
        if data_frame["sentiment_polarity"][i] == 0:
            neutral += data_frame["wgt"][i]
        elif 0 < data_frame["sentiment_polarity"][i] <= 0.3:
            w_positive += data_frame["wgt"][i]
        elif 0.3 < data_frame["sentiment_polarity"][i] <= 0.6:
            positive += data_frame["wgt"][i]
        elif 0.6 < data_frame["sentiment_polarity"][i] <= 1:
            s_positive += data_frame["wgt"][i]
        elif -0.3 < data_frame["sentiment_polarity"][i] <= 0:
            w_negative += data_frame["wgt"][i]
        elif -0.6 < data_frame["sentiment_polarity"][i] <= -0.3:
            negative += data_frame["wgt"][i]
        elif -1<= data_frame["sentiment_polarity"][i] <= -0.6:
            s_negative += data_frame["wgt"][i]
    #overall sentiment for a phase is the weighted average for all the individual tweet sentiments
    overall_sentiment=avg_sentiment/wgt_sum
    positive=(positive/wgt_sum)*100
    negative=(negative/wgt_sum)*100
    neutral=(neutral/wgt_sum)*100
    s_positive=(s_positive/wgt_sum)*100
    s_negative=(s_negative/wgt_sum)*100
    w_positive=(w_positive/wgt_sum)*100
    w_negative=(w_negative/wgt_sum)*100
    #writing into the file "the percentage of all the sentiment categories for a phase
    file_writer.writerow({'Phase_Name':phase, 'Positive(%)': positive,'Negative(%)':negative,'Weakly Negative':w_negative,"Weakly Positive":w_positive,"Strongly Negative":s_negative,"Strongly Positive":s_positive,"Neutral":neutral,"Overall_sentiment":overall_sentiment})
    

#This function filters the tweet according to our relevance and finds the sentiment by textblob
def find_sentiment(phase,writer,writer_1):
    data_frame = pd.read_csv(fr"IBM HACK CHALLENGE DATA\{phase}\final_cleaned_data.csv",engine="python")
    from ast import literal_eval
    data_frame.dropna(inplace=True)
    data_frame['Actual Tweet'] = data_frame['Actual Tweet'].apply(literal_eval)
    #filtering out the tweets whose text contains the keyword lockdown
    data_frame= data_frame[data_frame['cleaned_text'].str.lower().str.contains('lockdown')]
    print(phase)
    #finding sentiment for a cleaned tweet text by using TextBlob
    data_frame["sentiment_polarity"]=data_frame.apply(lambda x:get_textblob_sentiment(x["cleaned_text"]).polarity, axis=1)
    data_frame["sentiment_subjectivity"] = data_frame.apply(lambda x:get_textblob_sentiment(x["cleaned_text"]).subjectivity, axis=1)
    #factual information is discarded by this step
    data_frame=data_frame[data_frame["sentiment_subjectivity"]>0.5]
    for index in data_frame.index:
        # writing the individual tweet sentiments and the timestamp of the tweet in each phase into the file
        writer_1.writerow({"created_at": data_frame["Actual Tweet"][index]["created_at"],"sentiment": data_frame["sentiment_polarity"][index]})
    plot_overall_sent(data_frame,writer)
#This function calls the TextBlob function to find the sentiment object
def get_textblob_sentiment(tweetText):
    return TextBlob(tweetText).sentiment
if __name__ == "__main__":
    with open('plot_data.csv', 'w', newline='') as file,open('plot_data_1.csv', 'a', newline='') as file1:
        fieldnames = ['Phase_Name', 'Positive(%)','Negative(%)',"Weakly Negative","Weakly Positive","Strongly Negative","Strongly Positive","Neutral","Overall_sentiment"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        fieldnames_1 = ['created_at', 'sentiment']
        writer_1 = csv.DictWriter(file1, fieldnames=fieldnames_1)
        writer_1.writeheader()
        for phase in ["BEFORE LOCKDOWN DATA","PHASE 1","PHASE 2","PHASE 3","PHASE 4","UNLOCK 2.0 LAST 4 DAYS DATA(7,8,9,10 JULY)"]:
           find_sentiment(phase,writer,writer_1)