QA-spider
=========

Question-Answer based net spider. To use to user data from SNS to improve the accurancy of Q&A systems such Quara, Yahoo Answer, Baidu Zhidao and so on. The speder is designed to provide the Q&A system with more user information to specify which group to identify for the problems user asked. 

The first step is to combine the user data between SNS and Q&A system

##  Fetech the user data of following websites 

* Twitter
* Sina Weibo
* Facebook

## Fetech the data of question and answer of the following websites 

* Yahoo Answer
* Quara
* Baidu Zhidao

### TODO LIST
* using stack_twitter link file to get twitter user data

### Things need to be done 
* [X] let the script of getting twitter data support multi-process run(make it faster)
    * [X] add twitter user accounts and oauth the application
        *  qaspider[1-20]@126.com
        * twitter-user-name: qaspider1, qspider2, qaspider3, qaspider4, qaspider5
    * [X] multi-thread process
* [ ] mark the best answer
* [ ] change develop environment to Java
* [ ] crawl the data from: http://www.brianbondy.com/stackexchange-twitter/stackoverflow/
* [o] Improve the twitter-tool set to crawl Quora dataset.
    * [X] Twitter Streaming API only gets the data after the connecttion, which means it is more suitable for apps that wants to be notified when something happens. API cannot retrival the data of past time. This way is blocked.
    * [ ] try request ajax(PlantomJS?). Have not try
    * [X] filter the question whose numbers of answers is above 0.
    * [o] use multiple authentication keys and tokens(divide the data file into several parts).
        * [X] add four users in archeever and three users in follow.py
        * [ ] can break the api rate limit but the scrawling speed is still not fast enough
        * [X] by pausing and resuming the process we can change the crawling script in a more dynamic way
* [ ] find another dataset besides Lazytweets.
* [ ] markup the best answer of Lazytweets mannually.
* [ ] Would use java in the future, build the java development environment.
* [ ] Learn about `Information Retrival`
* [ ] Maybe find a RA Job in the next year

* link Yahoo Answers data with twitter
* crawl the data from LazyTweet
* add category data for Yahoo Answer (set follow = True and callback together)

### Open Topics 
* different pipelines for different spiders: http://stackoverflow.com/questions/8372703/how-can-i-use-different-pipelines-for-different-spiders-in-a-single-scrapy-proje

## Development Log 

### 2013.10.3
* Write to extract quora link to get user data(link file)
 
### 2013.10.2
* set up the script of marking the best answer of lazytweet.
* Has crawled the whole twitter data of lazytweets(Including tweets and following information)

### 2013.9.29
* use multiple authentication keys and tokens(divide the data file into several parts).
* add four users in archeever and three users in follow.py
* can break the api rate limit but the scrawling speed is still not fast enough
* by pausing and resuming the process we can change the crawling script in a more dynamic way

### 2013.9.10 
* different spider, different pipeline, different file(based on their spider names)
* Refactor pipeline.py

### 2013.9.3 
* 

### 2013.9.2 
* change some file to integer
    * number of marks
 
### 2013.8.31 
* refresh the question item
    * add the category into the question_loader


### 2013.8.30 
* Add the categories of yahoo answers questions
* add best answers
* according to the requirement below, get the question and answer seperated
 
### 2013.8.29 
* [o] Install IPython to get the scrapy shell more powerful
    * [X] Install Anaconda
    * [X] install ipython
    * [ ] set ipython the default python console
 
* [ ] Select HTML elements with more than one css class using XPath
    * http://westhoffswelt.de/blog/0036_xpath_to_select_html_by_class.html
 
### Yahoo Answer Requirement 
All files are encoded using utf-8.

Format for CxxQuestion.dat
each line represents a question, containing the following fields separated by tab:

* QuestionID, a unique integer
* UrlOnYahoo, like '20080331094331AAwxUTw', and the actual full url is http://answers.yahoo.com/question/index?qid=20080331094331AAwxUTw
* Category, 
* AskerID, like 'LjOiBoZxaa', and the profile url for the user is http://answers.yahoo.com/my/profile?show=LjOiBoZxaa
* AskingDate
* QuestionTitle
* QuestionDescription
* NumberOfAnswers
* NumberOfInterestingMarks, representing how many users mark this question interesting 
* Status
* User
* ImportDate


Format for CxxAnswer.dat
each line represents an answer record, containing the following fields separated by tab:

- QuestionID, the integer of the question
- AnswerID, a unique integer
- AnswererID, the same as "AskerID" above
- AnsweringDate
- AnswerContent
- IsBestAnswer, 0 or 1, 1 means it is the best answer, chosen by asker
- RatingByAsker, Asker's rating, 0 ~ 5
- GoodMarkByUsers, how many users think this answer good
- BadMarkByUsers, how many users think this answer bad
- AnswererName

The QuestionIDs in answer file are arranged in the same order as QuestionIDs in question file.

Format for YahooCategoriesSorted.txt
each line represents a category on Yahoo! Answers, containing the following fields separated by colon:

- CategoryIDOnYahoo, like 396546444, and the page displaying resolved question on this page is http://answers.yahoo.com/dir/?link=over&sid=396546444
- NumberOfResolvedQuestions, how many resolved questions in this category
- CategoryName, like ,Travel,Asia Pacific,China
- IfContainsSubCategory, whether it contains any sub categories.

