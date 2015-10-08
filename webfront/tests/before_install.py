f = open("webfront/models.py","r")
text = ""
for line in f:
    text += line.replace("managed = False","managed = True")
f.close()
f = open("webfront/models.py","w")
print ("Config changed "+len(text.find_all("managed = True"))+ " times.")
f.write(text)
