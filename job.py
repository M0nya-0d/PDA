#Job
inc = None
file = open('inc.txt', 'r', encoding='utf-8')
inc = int(file.read())
file.close()

if(inc == 1):
    #inc = 50
    file = open('inc.txt', 'w', encoding='utf-8')
    file.write('55')
    file.close()
