#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import re
import codecs
import collections

db = MySQLdb.connect(host="localhost", user="root", passwd="123", db="onthobase", charset='utf8') 
cursor = db.cursor()

sql = """DELETE FROM OntRel"""
cursor.execute(sql)

msg = input("Enter class number: ")
words_in_class = collections.defaultdict(list)
subclasses_of_class = collections.defaultdict(list)
class_names = {}

pattern1 = re.compile(u'([А-Яа-я-]+)\s+', flags=re.U)               # pattern for word
pattern2 = re.compile(u'\s+\$(\d+)', flags=re.U)                    # pattern for class number
pattern3 = re.compile(u'\$(\d+)\s+', flags=re.U)                    # pattern for class number in class names
pattern4 = re.compile(u'([А-Яа-я-]+)\s\s\s', flags=re.U)            # pattern for last word of class name
pattern5 = re.compile(u'(\d+)/(\d+)/*(\d+)*/*(\d+)*/*(\d+)*')       # pattern for 4 * '/' 


fd = codecs.open("ClassifierUni.txt", "r", "utf-8")
rows = fd.readlines()
for row in rows:
    match3 = pattern3.search(row)
    match4 = pattern4.search(row)
    if match3 == None or match4 == None:
        continue
    else:
        class_names[match3.group(1)] = match4.group(1)              # dict name of classes--- class number : final name of class


f = codecs.open("SLOVAR.txt", "r", "utf-8")
lines = f.readlines()
for line in lines:
    match1 = pattern1.search(line)
    match2 = pattern2.search(line)
    if match1 == None or match2 == None:
        continue
    else:
        words_in_class[match2.group(1)].append(match1.group(1))    # dict words of classes--- class number: list of words (only high-level classes without '/')
        class_len = len(match2.group(1))                               # class number length
        for i in range(1, class_len):                 
            subclass = match2.group(1)[0:class_len-i]                  # form all subclasses for class
            if match2.group(1) not in subclasses_of_class[subclass]: 
                subclasses_of_class[subclass].append(match2.group(1))  # dict list of subclasses--- class : subclasses

    
    if match2.group(1) in class_names and str(msg) == str(match2.group(1)):
        sql = """INSERT INTO OntRel(Meaning_ID1, Relation, Meaning_ID2)
	VALUES ('%(Meaning_ID1)s', '%(Relation)s', '%(Meaning_ID2)s')
	"""%{"Meaning_ID1":match1.group(1), "Relation":'Gen', "Meaning_ID2": class_names[match2.group(1)]}
        cursor.execute(sql)


for i in range(0, len(subclasses_of_class[str(msg)])):             # insert all the subclasses as sub_name - relation - class
    #if subclasses_of_class[str(msg)][i] in class_names:
    #	sql = """INSERT INTO OntRel(Meaning_ID1, Relation, Meaning_ID2)
    #	VALUES ('%(Meaning_ID1)s', '%(Relation)s', '%(Meaning_ID2)s')
    #	"""%{"Meaning_ID1":class_names[subclasses_of_class[str(msg)][i]], "Relation":'Gen', "Meaning_ID2": class_names[str(msg)]}
    #	cursor.execute(sql)     
    for m in range(0, len(words_in_class[subclasses_of_class[str(msg)][i]])):   # insert all the words of subclasses - relation - class 
	sql = """INSERT INTO OntRel(Meaning_ID1, Relation, Meaning_ID2)        
	VALUES ('%(Meaning_ID1)s', '%(Relation)s', '%(Meaning_ID2)s')
	"""%{"Meaning_ID1":words_in_class[subclasses_of_class[str(msg)][i]][m], "Relation":'Gen', "Meaning_ID2": class_names[str(msg)]}
	cursor.execute(sql)                                                    

db.commit() 

sql = """SELECT * FROM OntRel"""
cursor.execute(sql)
result = cursor.fetchall()

doc = codecs.open("onthology.txt", "w", "utf-8")

for i in result:
    for m in i:
        doc.write(m + "\t")
    doc.write("\n")

doc.close()


