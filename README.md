QA-spider
=========

Question-Answer based net spider. To use to user data from SNS to improve the accurancy of Q&A systems such Quara, Yahoo Answer, Baidu Zhidao and so on. The speder is designed to provide the Q&A system with more user information to specify which group to identify for the problems user asked. 

The first step is to combine the user data between SNS and Q&A system

==  Fetech the user data of following websites ==

* Twitter
* Sina Weibo
* Facebook

== Fetech the data of question and answer of the following websites ==

* Yahoo Answer
* Quara
* Baidu Zhidao

== Development Log ==

=== 2013.8.31 ===
* change some file to integer
    * number of marks
=== 2013.8.31 ===
* refresh the question item
    * add the category into the question_loader


=== 2013.8.30 ===
* Add the categories of yahoo answers questions
* add best answers
* according to the requirement below, get the question and answer seperated
 
=== 2013.8.29 ===
* [o] Install IPython to get the scrapy shell more powerful
    * [X] Install Anaconda
    * [X] install ipython
    * [ ] set ipython the default python console
 
* [ ] Select HTML elements with more than one css class using XPath
    * http://westhoffswelt.de/blog/0036_xpath_to_select_html_by_class.html
 
=== Yahoo Answer Requirement ===
All files are encoded using utf-8.

Format for CxxQuestion.dat
each line represents a question, containing the following fields separated by tab:

(0) QuestionID, a unique integer
(1) UrlOnYahoo, like '20080331094331AAwxUTw', and the actual full url is http://answers.yahoo.com/question/index?qid=20080331094331AAwxUTw
(2) Category, 
(3) AskerID, like 'LjOiBoZxaa', and the profile url for the user is http://answers.yahoo.com/my/profile?show=LjOiBoZxaa
(4) AskingDate
(5) QuestionTitle
(6) QuestionDescription
(7) NumberOfAnswers
(8) NumberOfInterestingMarks, representing how many users mark this question interesting 
(9) Status
(10) User
(11) ImportDate


Format for CxxAnswer.dat
each line represents an answer record, containing the following fields separated by tab:

(0) QuestionID, the integer of the question
(1) AnswerID, a unique integer
(2) AnswererID, the same as "AskerID" above
(3) AnsweringDate
(4) AnswerContent
(5) IsBestAnswer, 0 or 1, 1 means it is the best answer, chosen by asker
(6) RatingByAsker, Asker's rating, 0 ~ 5
(7) GoodMarkByUsers, how many users think this answer good
(8) BadMarkByUsers, how many users think this answer bad
(9) AnswererName

The QuestionIDs in answer file are arranged in the same order as QuestionIDs in question file.

Format for YahooCategoriesSorted.txt
each line represents a category on Yahoo! Answers, containing the following fields separated by colon:

(0) CategoryIDOnYahoo, like 396546444, and the page displaying resolved question on this page is http://answers.yahoo.com/dir/?link=over&sid=396546444
(1) NumberOfResolvedQuestions, how many resolved questions in this category
(2) CategoryName, like ,Travel,Asia Pacific,China
(3) IfContainsSubCategory, whether it contains any sub categories.

