#%%
from datetime import datetime, timedelta
import datetime
import datetime as dt
from threading import Thread
import time
import requests
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

ID_TELEGRAM = 'Your ID'
#%%
START_TIME = time.time()
BASE_URL = f'https://es.investing.com/economic-calendar/'
MONTHS = 100

def scrap_even_days(events,chrome2):
    for fecha in range(len(fechas), 1, -1):
        if fecha % 2 == 0:
            print(f'Fecha desde {fechas[fecha]} hasta {fechas[fecha-1]}')        
            chrome2.get(BASE_URL)
            #print(f'Missing {fecha} of {len(fechas)}, eventos registrados: {len(events)}')
            names = get_following(chrome2, fechas[fecha], fechas[fecha-1])
            events = events + names
            print(events[-1:])
    
    
def scrap_odd_days(events, chrome):
    for fecha in range(len(fechas)-1, 1, -1):
        if fecha % 2 != 0:      
            chrome.get(BASE_URL)
            print(f'Fecha desde {fechas[fecha]} hasta {fechas[fecha-1]}')
            #print(f'Missing {fecha} of {len(fechas)}, eventos registrados: {len(events)}')
            names = get_following(chrome, fechas[fecha], fechas[fecha-1])
            events = events + names
            print(events[-1:])



def scrap(events):
    for fecha in range(len(fechas)-1, 1, -1):
        with webdriver.Chrome(options=options) as chrome2:
            print(f'Fecha desde {fechas[fecha]} hasta {fechas[fecha-1]}')        
            chrome2.get(BASE_URL)
            #print(f'Missing {fecha} of {len(fechas)}, eventos registrados: {len(events)}')
            events = get_following(chrome2, fechas[fecha], fechas[fecha-1])
            #names = get_following(chrome2, fechas[fecha], fechas[fecha-1])
            #events = events + names

            #print(events[-1:])
            send_message('Recolección de eventos completada')
            return events
        
    
def send_message(message, chat_id = ID_TELEGRAM):
    requests.post('https://api.telegram.org/Your_bot:YourAPI/sendMessage',
            data={'chat_id': chat_id, 'text': message})   


def start_driver():
    '''Starts the driver when using parallel programming'''
    options = Options()
    options.add_argument("--disable-notification")
    options.add_argument("--disable-infobars")
    options.add_argument("--mute-audio")
    #options.add_argument("--disable-gpu")
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1200,1000')
    options.add_argument('--disable-dev-shm-usage')
    #options.add_argument("user-data-dir=.") 
    #options.add_argument('--lang=en-US')
    #options.add_argument("headless")

    driver = webdriver.Chrome(options=options)
    return driver


def get_following(chrome, fini, ffin):
    
    fini = datetime.datetime.strftime(fini, '%d/%m/%Y')
    ffin = datetime.datetime.strftime(ffin, '%d/%m/%Y')
    print(f'Getting economic calendar from {BASE_URL}')

    
    
    cal = chrome.find_element(By.ID, 'datePickerToggleBtn')
    cal.click()
    time.sleep(2)
    start_date = chrome.find_element(By.XPATH, '//*[@id="startDate"]')
    start_date.clear()
    start_date.send_keys(f'{fini}')
    end_date = chrome.find_element(By.XPATH, '//*[@id="endDate"]')
    end_date.clear()
    end_date.send_keys(f'{ffin}')
    time.sleep(2)
    
    chrome.find_element(By.XPATH, '//*[@id="applyBtn"]').click()
    
    time.sleep(2)
    chrome.find_element(By.XPATH, '//*[@id="filterStateAnchor"]').click()
    time.sleep(3)
    
    chrome.find_element(By.XPATH, '//*[@id="importance2"]').click()
    chrome.find_element(By.XPATH, '//*[@id="importance3"]').click()
    time.sleep(1)
    chrome.find_element(By.XPATH, '//*[@id="ecSubmitButton"]').click()
    time.sleep(1)
    
    economic_calendar_loading = chrome.find_element(By.ID, 'economicCalendarData')

    #scroll_bar = chrome.find_element(By.XPATH, "/html/body/div[6]/div/div/div/div[3]") 
    #last_ht, ht = 0, 1
    #start_time = datetime.datetime.now()
    #scrapping_time = start_time + timedelta(seconds=38)
    """while datetime.datetime.now() < scrapping_time:
    time.sleep(0.5)
    #ht = chrome.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    #ht = chrome.execute_script(""" 
    #arguments[0].scrollTo(0, arguments[0].scrollHeight); 
    #return arguments[0].scrollHeight; """, scroll_bar)
    #ht = chrome.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #ht = chrome.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", economic_calendar_loading)
    #ht = chrome.execute_script("arguments[0].scrollIntoView(false);", economic_calendar_loading)
    cleaned_events = []
    #events = economic_calendar_loading.find_elements(By.TAG_NAME, 'tr')
    dates = economic_calendar_loading.find_elements(By.CLASS_NAME, 'theDay')
    events = economic_calendar_loading.find_elements(By.CLASS_NAME, 'js-event-item')
    time.sleep(2)
    i = 0
    ultima_hora = '03:00'
    
    for evento in events:
        columns = evento.find_elements(By.TAG_NAME, 'td')
        #ultima_hora = dt.datetime.strptime('00:00', '%H:%M')
        #print(evento)
        #column_name = evento.find_element_by_tag_name('th').text
        hora = columns[0].text
        print(f'Ultima hora: {ultima_hora}, hora: {hora}')
        if hora < ultima_hora:
            i += 1
        ultima_hora = hora
        divisa = columns[1].text
        importancia = columns[2].text
        evento = columns[3].text
        actual = columns[4].text
        prevision = columns[5].text
        anterior = columns[6].text
        _ = columns[7].text
        fecha = dates[i].text
        
        cleaned_events.append([fecha, hora, divisa, importancia, evento, actual, prevision, anterior])
    #events = [event.text for event in events if event.text != '']
    return cleaned_events



fechas = []
events = []
now = datetime.date.today() + timedelta(days=30)
month = now
fechas.append(month)

for i in range(3):
    month = month - timedelta(days=30)
    fechas.append(month)


options = Options()
options.add_argument("--disable-notification")
options.add_argument("--disable-infobars")
options.add_argument("--mute-audio")
#options.add_argument("--disable-gpu")
#options.add_argument('--no-sandbox')
options.add_argument('--window-size=1200,1000')
options.add_argument('--disable-dev-shm-usage')
#options.add_argument("user-data-dir=.") 
#options.add_argument('--lang=en-US')
#options.add_argument("headless")

#driver2 = start_driver()
#thread_2 = Thread(target=scrap_odd_days, args=(events,driver2))

#thread_2.daemon = True
#thread_2.start()
events = scrap(events)

#thread_2.join()

print(f"Running time: {int((time.time() - START_TIME)/60)} minutes and {(time.time() - START_TIME)%60} seconds")
# %%
import pandas as pd
events = pd.DataFrame(events, columns=['Fecha','Hora', 'Divisa', 'Importancia', 'Evento', 'Actual', 'Prevision', 'Anterior'])

# %%
events
# %%
events.to_csv('events.csv')
# %%
algo = dt.datetime.strptime('00:00', '%H:%M')
# %%
