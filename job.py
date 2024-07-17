#Job
file = open('inc.txt', 'r', encoding='utf-8')
inc = int(file.read())
file.close()

if(inc == 1):
  global inc
  inc = 50
  file = open('inc.txt', 'w', encoding='utf-8')
  file.write('0')
  file.close()
