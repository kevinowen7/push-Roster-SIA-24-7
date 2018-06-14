from selenium import webdriver
 
driver = webdriver.Chrome('C:/chromedriver.exe')
driver.get('https://web.whatsapp.com/')
 
name =['Mami1']
msg = ('Ini pesan dari program otomatis jason sorongan (tidak perlu dibalas)')
 
input('Enter anything after scanning QR code')


for i in range(0,len(name)):
	user = driver.find_element_by_xpath('//span[@title = "{}"]'.format(name[i]))
	user.click()
	msg_box = driver.find_element_by_class_name('_2S1VP')
	msg_box.send_keys(msg)
	button = driver.find_element_by_class_name('_2lkdt')
	button.click()
	i=i+1
