#Job
inc = None
file = open('inc.txt', 'r', encoding='utf-8')
inc = int(file.read())
file.close()
print(inc)
while True:
    if(inc == '1'):
        file = open('inc.txt', 'w', encoding='utf-8')
        file.write('55')
        file.close()
        print(inc)
