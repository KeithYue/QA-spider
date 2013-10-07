import os
follow_dir = './data/twitter-follow/'

for file_name in os.listdir(follow_dir):
    print file_name
    file = open(os.path.join(follow_dir, file_name), 'r')
    for line in file.readlines()[1:]:
        twitter_name = line.split()[-1]
        os.system('./archiver_beta1.py -o %s -s %s' % (twitter_name, './data/tweets/'))
