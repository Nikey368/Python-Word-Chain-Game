import enchant
import time
import math
import shelve
import difflib
import MeCab
from wordfreq import zipf_frequency

d = shelve.open('score.txt')  # here you will save the score variable
d["Nobody"] = 0
words = []
mostCommon = []

SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}
def ordinal(num):
    # I'm checking for 10-20 because those are the digits that
    # don't follow the normal counting scheme. 
    if 10 <= num % 100 <= 20:
        suffix = 'th'
    else:
        # the second parameter is a default.
        suffix = SUFFIXES.get(num % 10, 'th')
    return str(num) + suffix

"""with open("words_alpha.txt",encoding='utf-8') as file:
    for line in file:
        words.append(line.rstrip())
with open("10000_common_english_words.txt",encoding='utf-8') as file:
    for line in file:
        mostCommon.append(line.rstrip())"""      

while True:
    print(enchant.list_languages())
    lang = input("Lanugage?: ")
    if len(lang) >= 5:
        lang = lang[0:-2] + lang[-2:].upper()
    langsuggest = difflib.get_close_matches(lang, enchant.list_languages(),100,0.6)
    if lang in enchant.list_languages():
        break
    elif len(langsuggest) > 0:
        langsuggest = difflib.get_close_matches(lang, enchant.list_languages(),100,0.6)
        for x in langsuggest:
            confirm = input("Did you mean "+x+"? Type 'n' if no. ")
            if confirm != "n":
                lang = x
                break
        else:
            continue
        break
    print("That is invalid")
dic = enchant.request_dict(lang)

while True:
    startingWord = input("What is your starting word? ")
    if startingWord == "" or startingWord == None:
        print("Type something.")
        continue
    if dic.check(startingWord):
        break
    elif startingWord == "DEBUGMODE":
        action = input("What would you like to do? ")
        if action == "CLEARSCORES":
            d.close()
            d = shelve.open('score.txt', flag='n')
            d["Nobody"] = 0
            print("Scores cleared")
            continue
        elif action == "SEESCORES":
            for i in d:
                print(i+": "+str(d[i]))
            continue
    print("That is not a valid word.")
    suggestions = dic.suggest(startingWord)
    if len(suggestions) > 1:
        print("Did you mean: "+suggestions[0]+"?")


wordsUsed = [startingWord]
wordChain = startingWord

wordToCheck = startingWord
failureReason = "wrongSpelling"

fullWordLength = len(startingWord)
minWordLength = 0

startingTime = time.time()
timeSoFar = 0

points = 0
timeCombo = 0

while True:
    newWord = input("Give me a word that starts with the letter '"+wordToCheck[-1]+"' and is at least "+str(minWordLength)+" letters long: ")
    timeTookToAnswer = time.time() - (timeSoFar + startingTime)
    timeSoFar = time.time() - startingTime
    wordWorks = True
    if lang == "sfvaervaevae":
        """oldwordresult = kks.convert(wordToCheck)
        newwordresult = kks.convert(newWord)
        possibleLetters = []
        for item in oldwordresult:
            possibleLetters"""
    else:
        wordWorks = (newWord[0] == wordToCheck[-1])
    if newWord != None and newWord != "" and (not " " in newWord) and (dic.check(newWord)) and (not newWord in wordsUsed) and wordWorks and (len(newWord) >= minWordLength) and (timeTookToAnswer < 10):
        wordToCheck = newWord
        wordsUsed.append(newWord)
        wordChain += newWord[1:len(newWord)]
        fullWordLength += len(newWord)
        points += 1
        if len(newWord) > minWordLength + 5:
            bonus = len(newWord) - (minWordLength + 5)
            print("+"+str(bonus)+" bonus points (word length)")
            points += bonus
        if timeTookToAnswer < 2.5:
            bonus = 2 + math.floor(len(newWord) / 5)
            print("+"+str(bonus)+" bonus points (time to answer)")
            points += bonus
            if timeCombo > 0:
                bonus = timeCombo
                print("+"+str(bonus)+" bonus points (time streak)")
                points += bonus
            if timeCombo < 5:
                timeCombo += 1
        else:
            timeCombo = 0
        if zipf_frequency(newWord, lang[0:2]) < 4:
            bonus = math.floor(11 - pow(zipf_frequency(newWord, lang[0:2]),1.66))
            print("+"+str(bonus)+" bonus points (uncommon word)")
            points += bonus
        if (len(wordsUsed) % 5 == 0) and minWordLength < 10:
            minWordLength += 1
    else:
        if newWord == None or newWord == "":
            failureReason = "enteredNothing"
        elif (newWord[0] != wordToCheck[-1]):
            failureReason = "invalid"
        elif " " in newWord:
            failureReason = "noSpaces"
        elif (newWord in wordsUsed):
            failureReason = "alreadyUsed"
        elif (timeTookToAnswer >= 10):
            failureReason = "tooLong"
        elif (len(newWord) < minWordLength):
            failureReason = "tooShort"
        break

print("Game over!")
if failureReason == "wrongSpelling":
    suggestions = dic.suggest(newWord)
    if len(suggestions) > 1:
        print("Did you mean: "+suggestions[0]+"?")
    else:
        print(newWord+" is not a valid word.")
elif failureReason == "alreadyUsed":
    print("You already used the word '"+newWord+"'!")
elif failureReason == "invalid":
    print(newWord+" does not start with the letter '"+wordToCheck[-1]+"'!")
elif failureReason == "noSpaces":
    print("Spaces are not allowed")
elif failureReason == "tooShort":
    print(newWord+" is not "+str(minWordLength)+" or more letters long!")
elif failureReason == "tooLong":
    print("You took "+str(round(timeTookToAnswer,3))+" seconds to answer, "+str(round(timeTookToAnswer - 10,3))+" seconds more than you should.")
elif failureReason == "enteredNothing":
    print("You must enter something.")
else:
    print("I, uh, couldn't find out why you lost. Please contact the dev (me)")
print("You had "+str(points)+" points")
print("Your chain was "+str(len(wordsUsed))+" words long!")
print("It was "+str(fullWordLength)+" letters long")
print("Your final time was "+str(round(timeSoFar,3))+" seconds")
print("On average, you typed "+str(round((len(wordsUsed)-1)/(timeSoFar/60),2))+" words per minute")
print("Or "+str(round(fullWordLength/(timeSoFar),2))+" letters per second")
print("and the length of the average word was "+str(round(fullWordLength/len(wordsUsed),2)))
print("The final chain was:")
print(wordChain)
sortedHighScores = sorted(d.items(), key=lambda x:x[1], reverse=True)
highest = max(d.values())
bestperson = max(d, key=d.get)
print("The high score belongs to '"+str(bestperson)+"' with a score of "+str(highest))
closestname, closestvalue = min(d.items(), key=lambda x: abs(points - x[1]))
position = sortedHighScores.index((closestname, closestvalue))
print("You are closest to "+str(closestname)+", who is "+ordinal(position + 1)+" with their score of "+str(closestvalue))
if points > int(highest):
    name = input("You got the highscore! What is your name? If you do not wish to enter your score, leave this empty (If you already have submitted a score, you don't need to add the language code): ")
    if name != None and name != "":
        name = "("+lang[:2]+") "+name
        d[str(name)] = points
        print("The high score now belongs to '"+str(name)+"' with a score of "+str(points))
else:
    name = input("What is your name? If you do not wish to enter your score, leave this empty: ")
    if name != None and name != "":
        name = "("+lang[:2]+") "+name
        if not str(name) in d:
            d[str(name)] = points
        elif d[str(name)] < points:
            d[str(name)] = points
        sortedHighScores = sorted(d.items(), key=lambda x:x[1], reverse=True)
        position = sortedHighScores.index((name, d[str(name)]))
        print("Currently, you are "+ordinal(position + 1)+" with your score of "+str(d[str(name)]))
d.close()