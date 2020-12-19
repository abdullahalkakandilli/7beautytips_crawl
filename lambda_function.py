'''
   
Get inital datetime from beautytipsDate.txt - aws 3 --> last_execute

Get last_feed datetime from 7beautyTips rss --> last_feed

Compare last_execute & last_feed

Crawl web indexes after last_execute until last_feed from .rss

Write list to csv file

Upload csv file to Aws s3 Bucket

'''
import urllib.request
from bs4 import BeautifulSoup
import feedparser
import datetime
import boto3
import csv



def lambda_handler(event, context):
   
    s3 = boto3.client("s3")
    s3v2 = boto3.resource('s3')
    if event:
        #file_obj = event["Records"][0]
        bucketname = str("aws-crawl-trigger")
        
        fileObj = s3.get_object(Bucket=bucketname, Key="beautytipsDate.txt")
        file_content = fileObj["Body"].read().decode('utf-8')
   
    
        
        last_execute = datetime.datetime.strptime(file_content, '%a, %d %b %Y %H:%M:%S %z')
        #last_execute will come from aws S3 config datatime
        print("last execute log: ", last_execute)
        print("last feed log: ")
        feed = feedparser.parse('https://7beautytips.com/feed/')
        
        last_feed = datetime.datetime.strptime(feed.entries[0].published, '%a, %d %b %Y %H:%M:%S %z')
        #websites last entry's publish time - last_feed
        
        
        
        
        

        if last_execute == last_feed:
            print("all is update")   #if there is no new entry, exit script
            
        else:
            title_list = []
            link_list = []
            
            for entry in feed.entries:
                pub_date = datetime.datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
                print("pub date log: ", pub_date)
                test_log = entry.link
                if(pub_date > last_execute):
                    title_list.append(entry.title)
                    link_list.append(entry.link)
                    print("entry link log: ",test_log )
            
        body_list = []
        
        for val in link_list:
            full_para =""
            soup2 = BeautifulSoup(urllib.request.urlopen(val).read(),"html.parser")
            b_tags = soup2.find_all("p") #find all <p> items from html page resource
            
            for i in b_tags:
                #collecting paragraphs
                full_para = i.text + full_para
                
                
            body_list.append(full_para.strip())
    #--------------------------------------------------------------------#        
    feed = feedparser.parse('https://7beautytips.com/feed/')        
    key2 = 'beautytipsDate.txt'
    fileObj3 = s3.get_object(Bucket=bucketname, Key="beautytipsDate.txt")
    with open('/tmp/beautytipsDate.txt', 'w') as f:
        f.write(feed.entries[0].published)
       
    bucket = s3v2.Bucket(bucketname)
    bucket.upload_file('/tmp/beautytipsDate.txt',key2)
    
    #--------------------------------------------------------------------#
    
    key = 'beautytipsCrawl.csv'
    getfile = s3.get_object(Bucket=bucketname, Key="beautytipsCrawl.csv")
    #Only then you can write the data into the '/tmp' folder.
    rows = zip(title_list,link_list,body_list)
    with open('/tmp/beautytipsCrawl.csv', 'a') as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)
           
    #upload the data into s3
    bucket = s3v2.Bucket(bucketname)
    bucket.upload_file('/tmp/beautytipsCrawl.csv', key)
    
    
    
    
          
    
    
   

        

    
    
  
    
    
    
