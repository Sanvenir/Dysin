
import os  
for root, dirs, files in os.walk('.'):  
    for file in files:
        if file.endswith('.ui'):
            os.system('pyside-uic -o ui_%s.py %s' % (file.rsplit('.', 1)[0], file))   
