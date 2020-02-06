import base64
import csv
import pandas as pd
import PyPDF2


"""

archivo = open("pdText.txt", "r",encoding='utf-8')

words = {}
banned = ["1-","del",'','al','mi','me','de','la','le','a','una','une','u','y','mis','que','en','sino','no','sus','ya','él','su','sí',';','allí','así','con','e','es','las','los','o','por','se','un','el','lo','nos','como']
minWord = 5

for linea in archivo.readlines():
    temp = linea.lower().replace("•",'').replace(",",' ').replace(".",'').replace('"','').replace('\n',' ').replace("(",' ').replace(")", ' ').replace("”",' ').replace("/",' ').replace("*",'').replace("“",'').replace("?",'').replace("¿",'').replace(":",'').split(" ")
    for word in temp:
        word = word.strip()
        if word in banned:
            continue
        
        try:
            a = int(word)
            continue
        except ValueError:
            if(word in words):
                words[word] += 1
                continue
            words.update({word:1})

archivo.close() 

output = {}
for key in words:
    
    if words[key] >= minWord:
        output.update({key:words[key]})

print(output)

"""