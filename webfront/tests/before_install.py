f = open("webfront/models.py","r")
text = ""
for line in f:
    text += line.replace("managed = False", "managed = True")
f.close()
f = open("webfront/models.py","w")
if text.find("managed = True") != -1:
    print("Config changed ")
f.write(text)
