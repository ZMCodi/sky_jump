sentence = str(input("Enter a sentence: "))

numWords = len(sentence.split())

reversedSentence = sentence.split()[::-1]

capitalizedSentence = sentence.upper()

#checks if the letters in the sentence are vowels and replace with * if they are
vowels = ["a", "e", "i", "o", "u"]
sentenceList = list(sentence)

for i in sentenceList: 
    if (i in vowels):
        sentenceList[sentenceList.index(i)] = "*"

print("The word count is " + str(numWords))
print("The reversed sentence is: " + ' '.join(reversedSentence))
print("The capitalized string is: " + capitalizedSentence)
print("Vowels switched to asterisks(*): " + ''.join(sentenceList))
