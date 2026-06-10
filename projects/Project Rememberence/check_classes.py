content = open(r'D:\cards\AI Prompts\Oracle Project\Project Files\constants.js', 'r', encoding='utf-8').read()
start = content.find("const classData")
print(content[start:start+3000])
