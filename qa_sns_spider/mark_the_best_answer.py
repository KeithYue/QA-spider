# coding=utf-8
# Use this script to mark the best answer of questions that has answers in lazytweets
# just run once using screen to let it run permantly
# load marks -> read all questions -> get all answers related with this question -> mark the answer -> write to file
import json
import sys

questions_file = open('./data/lazytweet_questions_has_answers.json', 'r')
original_answers = open('./data/lazytweet_answers.json', 'r')
answer_file_output = open('./data/lazytweet_answers_with_marks.json', 'r+w')

# return the whole answers given a question id
def get_answers(question_id):
    answers = []
    original_answers.seek(0)
    for line in original_answers.readlines():
        answer_json = json.loads(line)
        if answer_json['question_id'] == question_id:
            answers.append(answer_json)
    return answers

# answer: dict object
def set_best_answer(answer):
    answer['is_best_answer'] = 1

def set_commom_answer(answer):
    answer['is_best_answer'] = 0

# list of answers to be writed
def write_answers(answers):
    for answer in answers:
       # encode to jsong
       answer_json = json.dumps(answer)
       answer_file_output.write(answer_json)
       answer_file_output.write('\n')

def main():
    for question_json in questions_file.readlines():
        question = json.loads(question_json)
        print 'Question: '
        print question['question_content'].encode('utf-8')
        answers = get_answers(question['question_id'])
        print '%d answers' % len(answers)
        for index, answer in enumerate(answers):
            print '%d: %s' % (index, answer['answer_content'])
            # set all the related answer to 0
            set_commom_answer(answer)

# if a question has only one answer, then it is the best answer
        if(len(answers) == 1):
            best_answer_index = 0
        else:
            best_answer_index  = input('Please input best answer number: ')
        if best_answer_index != -1:
            set_best_answer(answers[best_answer_index])
# write to file
        write_answers(answers)
        print '-'*30

# close files
    questions_file.close()
    original_answers.close()
    answer_file_output .close()

main()
