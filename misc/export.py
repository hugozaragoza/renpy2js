from ftplib import FTP

session = FTP('92.205.2.244', 'export@helpp.net', 'export___')
session.cwd('public_html')
session.cwd('story1')
file = open('test.txt', 'rb')  # file to send
session.storbinary('STOR test.txt', file)  # send the file
file.close()  # close file and FTP
print("EXPORT done.")
session.quit()
