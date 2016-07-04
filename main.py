# -*- coding: utf-8 -*-
"""
@title:       minireview

@description: registration-free open source text-based blind review system

@author:      Priyanka Mandikal and Jim Salsman

@version:     0.5-beta of June 28, 2016

@license:     Apache v2 or latest with stronger patent sharing if available.

@see          https://github.com/priyankamandikal/reviewsystem
              for a previous version.

#@wonder: whether those are all valid docstring @decorators
          and whether they are formatted correctly

###@@@: means places that I want to continue working on;
###: introduces comments that involve lower-priority work to be done
"""

from flask import Flask, render_template, redirect, url_for, \
                  request, flash, escape
from os import listdir, rename, path # for path.sep, .exists() & .getmtime()
from random import choice
from time import ctime
import re

recdir = 'records' + path.sep                     # data subdirectory

app = Flask(__name__) # create Flask WSGI application

app.secret_key = 'enable flash() session cookies' # does what that says

@app.route('/')
def index():
    return render_template('index.html')          # in templates subdirectory

def nextrecord():
    try:
        # search files in the records subdirectory to find the greatest number
        records = listdir(recdir)
        record = 1+int(max(records)[0:9])  # increment maximum
        ### todo: check for improperly named files        
        return format(record, '09')        # left-pad with zeros to 9 places
    except:
        return format(1, '09')             # first is 1, not 0

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if request.method == 'GET':
        return render_template('ask.html') # single textarea & submit button
    elif request.method == 'POST':
        question = request.form['question']    # escape() raw input
        regexp = r'((https|ftp|file|http)://(((?!</p>| )).)*)'
        question = re.sub(regexp,"<a href='\\1'>\\1</a>",question)
        iframeurl = request.form['iframeurl']
        ### todo: hyperlink URLs in raw input with e.g. <a href="URL">URL</a>
        ### also sanity-check size of question field
        fn = 'records' + path.sep + nextrecord() + 'qu' # new question filename
        # checking if the file exists should prevent overflow(?)
        if path.exists(fn):
            flash('Overflow: a billion questions is too many; sorry.')
            return redirect(url_for('index'))          # GET /
            ### RACE condition if two people call nextrecord() simultaniously
            ### ... maybe try adding the process ID to end of fn and renaming?
        
        f = open(fn, 'w')
        f.write(iframeurl+'\n'+question+'\n') ### only add \n if not already at end? & below
        f.close()
        flash('Thanks for the question.')  # displays in layout.html
        return redirect(url_for('index'))  # GET /

def getrecords():
    records = {} # use a dictionary of file numbers to lists of suffixes
    for fn in listdir(recdir):             ### handle bad filenames
        if not fn[0:9] in records:
            records[fn[0:9]] = [fn[9:]]     # create file number's initial list
        else:
            records[fn[0:9]].append(fn[9:]) # add file suffix to list
    return records

@app.route('/answer', methods=['GET', 'POST'])
def answer():
    if request.method == 'GET':
        records = getrecords()
        selected = {}
        for ns, l in records.items():       # iterate over filenumbers
            if ns in selected or 'd' in l:  #   and filename suffix [l]ist
                continue                    # already did this filenumber
            elif not 'a' in l:
                selected[ns] = 'a'          # question needs an answer
            elif not ('e' in l or 'o' in l):
                selected[ns] = 'r'          # answer needs review
            elif 'o' in l and not 't' in l:
                selected[ns] = 't'          # opposing review needs tie-breaker
        if len(selected) < 1:
            flash('No open questions remaining to answer or review.')
            return redirect(url_for('index'))
        chosen = choice(selected.keys())    # pick a question at random
        ### convert to round-robin instead of random choice
        needs = selected[chosen]            # type of response needed
        files = {}                          # files' contents in a suffix
        for suffix in records[chosen]:      # iterate over the files available
            f = open(recdir + chosen + suffix, 'r')
            files[suffix] = f.readlines()        # read textual contents of each
            f.close()
        return render_template('answer.html', record=chosen, response=needs,
                               files=files) # invoke the template
    elif request.method == 'POST':
        record = request.form['record']     # file number with zeroes
        response = request.form['response'] # [submit button] 1 of: a,e,o,te,to
        answer = request.form['answer']     # no escape(): templates not |safe
        regexp = r'((https|ftp|file|http)://(((?!</p>| )).)*)'
        answer = re.sub(regexp,"<a href='\\1'>\\1</a>",answer)
        ### todo: hyperlink URLs in raw input with e.g. <a href="URL">URL</a>
        if response in ['te', 'to']:        # tie breaker
            if path.exists(recdir + record + 't'):
                flash('Someone else just submitted that tiebreaker.')
                return redirect(url_for('index'))
                ###@@@ SLOW RACE: see below
            rename(recdir + record + 'o', recdir + record + 't')
            response = response[1]          # 2nd character
        fn = recdir + record + response     # filename ### sanity check?
        if path.exists(fn):                 # does file exist?
            flash('Someone else just submitted the requested response.')
            return redirect(url_for('index'))
            ###@@@ SLOW RACE: lock choice() responses below for some time?
        f = open(fn, 'w')
        f.write(answer+'\n') ### only add \n if not already at end?
        f.close()
        flash('Thank you for your response.') # displays in layout.html
        return redirect(url_for('index'))

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'GET':
        records = getrecords()              # hopefully populated dictionary
        selected = {}                       # empty dictionary (hash table)
        for ns, l in records.items():       # iterate over keys and values 
            if ns in selected or 'd' in l:  # already seen filenumber or done
                continue                    # skip when already done
            elif 'e' in l or 't' in l:      # endorsed or tie-broken
                selected[ns] = l            # add list as a dictionary entry
        if len(selected) < 1:
            flash('No recommendations remain to be implemented.')
            return redirect(url_for('index'))
        selection = choice(selected.keys()) # pick a random reviewed question
        suffixes = selected[selection]
        files = {}                              # to map file suffixes to text
        for suffix in suffixes:                 # iterate over available files
            f = open(recdir + selection + suffix, 'r')
            files[suffix] = f.readlines()            # read textual contents of each
            f.close()
        return render_template('recommend.html', record=selection, files=files) 
    elif request.method == 'POST':
        record = request.form['record']         # file num. w/zeroes ### check
        resolution = request.form['resolution'] # implementation, e.g. diff URL
        regexp = r'((https|ftp|file|http)://(((?!</p>| )).)*)'
        resolution = re.sub(regexp,"<a href='\\1'>\\1</a>",resolution)
        ### todo: hyperlink URLs in raw input with e.g. <a href="URL">URL</a>
        ### sanity-check size of resolution field; no escape() because no |safe
        fn = recdir + record + 'd'              # resolution filename
        if path.exists(fn):                     # does file exist?
            flash('Someone else just submitted another implementation.')
            return redirect(url_for('index'))
            ###@@@ SLOW RACE: see above
        f = open(fn, 'w')
        f.write(resolution+'\n') ### only add \n if not already at end?
        f.close()
        flash('Thank you for the implementation.') # displays in layout.html
        return redirect(url_for('index'))

@app.route('/inspect', methods=['GET']) # optional: ?q=searchstring&r=reviewer
def inspect():
    records = getrecords()
    if len(records) < 1:
        flash('No questions in system.')
        return redirect(url_for('index'))
    filenums = records.keys()              # assuming contiguity can't delete
    filemodtimes = []                      # all file modification times
    searchstring = request.args.get('q')   # search e.g. category in -q files
    stringtimes = {'q':[],'a':[],'e':[],'o':[],'t':[],'d':[]} # searchstring
    reviewer = request.args.get('r')       # search for reviewer in -a/e/o/t
    reviewtimes = {'a':[],'e':[],'o':[],'t':[]} # times for reviewer search
    reviewercount = 0                      # number of times reviewer appears
    revieweragree = 0                      # times reviewer was agreed with
    reviewerdised = 0                      # times reviewer was opposed
    for fn in filenums:
        stringhit = False                  # flag whether searchstring is seen
        if searchstring:
            f = open(recdir + fn + 'q', 'r') # check question files
            question = f.read()
            f.close()
            if searchstring in question:   # substring search
                stringhit = True           # question has string
        for suffix in records[fn]:         # iterate over the files available
            modtime = path.getmtime(recdir + fn + suffix) # file modification
            filemodtimes.append(modtime)
            if stringhit:
                stringtimes[suffix].append(modtime)
            if reviewer and suffix in ['a', 'e', 'o', 't']:
                f = open(recdir + fn + suffix, 'r')
                contents = f.read()        # look for the reviewer argument
                f.close()
                if reviewer in contents:         # substring search
                    reviewercount = reviewercount + 1
                    reviewtimes[suffix].append(modtime) # store time
                    if suffix == 'a':            # reviewer answered
                        if 'e' in records[fn]:   # answer endorsed
                            revieweragree = revieweragree + 1
                        elif 'o' in records[fn]: # answer opposed
                            reviewerdised = reviewerdised + 1
                    elif suffix == 't':          # opposition was tiebroken
                        if 'o' in records[fn]:   # opposition agreed to
                            revieweragree = revieweragree + 1
                        elif 'e' in records[fn]: # opposition rejected
                            reviewerdised = reviewerdised + 1
    # summary statistics
    count, first, last = len(records), min(filenums), max(filenums)
    mindate, maxdate = min(filemodtimes), max(filemodtimes)
    meandate = sum(filemodtimes) / len(filemodtimes)
    return render_template('inspect.html', count=count, first=first, 
        last=last, mindate=ctime(mindate), maxdate=ctime(maxdate), 
        meandate=ctime(meandate),
        searchstring=searchstring, stringqs=stringtimes['qs'],
        stringas=stringtimes['a'], stringes=stringtimes['e'],
        stringos=stringtimes['o'], stringts=stringtimes['t'],
        stringds=stringtimes['d'], reviewer=reviewer, 
        revas=stringtimes['a'], reves=stringtimes['e'],
        revos=stringtimes['o'], revts=stringtimes['t'],
        reviewercount=reviewercount, revieweragree=revieweragree, 
        reviewerdised=reviewerdised)

#@app.errorhandler(404)
#def not_found(error):
#    return render_template('error.html'), 404

if __name__ == '__main__':
    app.run(
      use_reloader = True # reloads this source file when changed
    , use_debugger=True # see http://flask.pocoo.org/docs/0.11/errorhandling/
           )                    # runs on http://127.0.0.1:5000/

# end

