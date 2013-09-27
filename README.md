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

## Development Log 

### Things need to be done 
* [ ] Improve the twitter-tool set to crawl Quora dataset.
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

