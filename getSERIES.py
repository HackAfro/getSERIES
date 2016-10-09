# -*- coding: utf-8 -*-

#getSERIES.py - Checks for the latest episodes of your favourite tv-series and downloads them


"""
Copyright {2016} {HackAfro}

Licensed under the Apache License, Version 2.0 
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
"""
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os,webbrowser,requests,bs4
from sys import argv
from tkinter import ttk
from tkinter import messagebox
from tkinter import * 
from socket import gaierror
import time
import selenium
from PIL import Image,ImageTk

#Globals--------------------------------------------------------------------------------------------------------------------------------
root = None    
lst = None      
serie_entry = None    
int_var = None
serie_combo= None
season_max = None
season_entry= None
episode_max = None
season1 =None
retry = None
down_but=None
max_seas = None
max_epi = None
the_episodes = {}
seasons = []
episode_entry = None
get_img = None
img_src=None
#------------------------------------------------------------------------------------------------------------------------------------------
firefox_capabilities = DesiredCapabilities.FIREFOX
firefox_capabilities['marionette'] = True
firefox_capabilities['binary'] = 'C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe'

#---------------------------------------------------------------------------------------------------------------------------------------------------
if os.path.exists('gslogs.txt'):
  pass
else:
  logs = open('gslogs.txt','w')
  logs.close()
#----------------------------------------------------------------------------------------------------------------------------------------------------                

#Adds the driver path to the system PATH based on the browsers installed-----------------------------------------
def driver_path():
  folder = os.getcwd()
  paths = {'IE': ';' + folder + '\\selenium\\IE\\',
                    'Firefox' : ';' + folder + '\\selenium\\Firefox\\',
                    'Opera': ';' + folder + '\\selenium\\Opera\\',
                    'Chrome': ';' + folder + '\\selenium\\Chrome\\'}

  driverType = drivers()
  os.environ['path'] += paths[driverType]
  
  return driverType
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Function to check for latest episodes--------------------------------------------------------------------------------------------------------

def check(url):
  global season_max
  global episode_max
  global season1
  global get_img
  global the_episodes
  global img_src
  
  
  try:
    log = open('gslogs.txt','a')
    season_page = requests.get(url)  #gets the page your tv-serie
    soup = bs4.BeautifulSoup(season_page.text,'html.parser')
    links = soup.select('.data a')  #gets the link for all seasons
    imgs = soup.select('.img img')#get the link for imgs

    img_src = imgs[0].get('src')
    get_img = requests.get(img_src)
    
    for link in links:
      seasons = requests.get(link.get('href'))
      soupe = bs4.BeautifulSoup(seasons.text,'html.parser')
      selector = soupe.select('.data a')
      the_episodes['Season-'+link.getText()[7:10]] = selector[0].getText()

   #gets the latest season
    season1 = links[0].getText()
    season_max = int(season1[-2:]) + 1
    
    
     #checks for latest episode in latest season
    episode_page = requests.get(links[0].get('href'))
    soup1 = bs4.BeautifulSoup(episode_page.text,'html.parser')
    episode_links = soup1.select('.data a')  #gets the link for all episodes
    episode1 = episode_links[0].getText()
    episode_max = int(episode1[8:11]) + 1
    
    link_list = [link.getText() for link in episode_links] #creates a list with all the episodes
    
    #returns the recent episode
    latest_episode = link_list[0]
    
    return(latest_episode)
  except (ConnectionResetError,requests.packages.urllib3.exceptions.ProtocolError,
          requests.exceptions.ChunkedEncodingError,
          requests.exceptions.ConnectionError,ConnectionError,
          requests.packages.urllib3.exceptions.MaxRetryError,
          requests.packages.urllib3.exceptions.NewConnectionError,gaierror) as e:
    return 'Connection failed'
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    
# Function that downloads requested episode--------------------------------------------------------------------------------------------------------------------------------------------------------------

def download(*args):
  try:
    log = open('gslogs.txt','a')
    episode = args[2]
    latest_episode = check(args[0])
    
    if latest_episode.endswith('Season Finale'):
      latest_episode = latest_episode.replace('-',' ')
      new_lat_epi = latest_episode.split()
      epi_join = '-'.join(new_lat_epi)

      if episode == epi_join[:10].lower():
        episode=epi_join
        
    while latest_episode == 'Connection failed':
      log.write('Connection error'+'\n')
      retry=messagebox.askretrycancel('Connection Error','Connection Failed. Reconnect and try again' )
      if retry == True:
        continue
      else:
        break
    else:

      try:
        #checks to see if the requested episode is available
        num = latest_episode[8:11]
        if int(args[2][8:11]) > int(num) :
            retry = messagebox.showerror('Download Error','Episode not available. Use the Check button to make sure the episode is available')

        else:
           #puts the required season and episode in the url to get the episode page
          url_list = list(args[0])
          season  = args[1] +'/'
          url_list.insert(-11,(season + episode + '/'))
          download_page = requests.get(''.join(url_list))
          soup = bs4.BeautifulSoup(download_page.text,'html.parser')
          links = soup.select('.data a') #gets the link for all downloadable episode formats
          re_episode = links[1].get('href')

          #checks to see if internet download manager is installed on the system. If it is, it uses IDM to download episode.
          if os.path.exists('C:\Program Files (x86)\Internet Download Manager'):
            webbrowser.open(re_episode) #opens webbrowser to download requested episode

          #otherwise, it downloads it saves it to the folder chosen
          else:
            messagebox.showinfo('Save', 'Please select the destination folder')
            folder = filedialog.askdirectory()

            season_text=seaS()[0].lower()+seaS()[-2:]
            episode_text = epiSeas()[0]+epiSeas()[-2:]
            name = tvres() + '-' + season_text + episode_text
  
            save_folder = os.path.join(folder,name+'.mp4')
            messagebox.showinfo('Download','Download started. Please be patient. Press the OK button')

            get_epi = requests.get(re_episode)
            with open(save_folder,'wb') as save:
              for chunks in get_epi.iter_content(1000):
                save.write(chunks)
              

            messagebox.showinfo('Download','Download Completed')
            
          
      except(ValueError,IndexError) as er:
        messagebox.showerror('Download Error','Episode not available. Use the Check button to make sure the episode is available')
          
  except (ConnectionResetError,requests.packages.urllib3.exceptions.ProtocolError,
          requests.exceptions.ChunkedEncodingError,
          requests.exceptions.ConnectionError,ConnectionError,
          requests.packages.urllib3.exceptions.MaxRetryError,
          requests.packages.urllib3.exceptions.NewConnectionError,gaierror) as e:
    messagebox.askretrycancel('Connection Error','Connection failed. Reconnect and try again')
  log.close()
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def hdCheck(tv_serie,season=None):
  global max_seas
  global max_epi
  global seasons

  try:
    url = 'http://www.todaytvseries.com'
    word = ''

    with open('today.txt','r') as today:
      series = [serie_url.strip('\n') for serie_url in today.readlines() if tv_serie in serie_url]

    for serie in series:
      word= serie

    serie_page = url+word
    page = requests.get(serie_page)
    soup = bs4.BeautifulSoup(page.text,'html.parser')
    episodes = soup.select('.row2.footer')
    if season != None:
      try:
        seasons = [link.getText()[0:6] for link in episodes if season in link.getText()[0:6]]
        max_epi =  int(seasons[0][4:6])+1
      except IndexError:
        messagebox.showerror('Error','Requested season not yet available')
    try:
      epi_text = episodes[0].getText()
      max_seas = int(episodes[0].getText()[1:3])+1
    except ValueError:
      pass
    
  except (ConnectionResetError,requests.packages.urllib3.exceptions.ProtocolError,
          requests.exceptions.ChunkedEncodingError,
          requests.exceptions.ConnectionError,ConnectionError,
          requests.packages.urllib3.exceptions.MaxRetryError,
          requests.packages.urllib3.exceptions.NewConnectionError,gaierror,AttributeError) as e:
    return 'Connection failed'
    
#HD-series-downloader----------------------------------------------------------------------------------------------------------------
def todaySeries(*args):
  global logs
  try:
    tv_serie = args[0].lower()
    episode = args[1]
    url = 'http://www.todaytvseries.com'
    word = ''

    with open('today.txt','r') as today:
      series = [serie_url.strip('\n') for serie_url in today.readlines() if tv_serie in serie_url]

    for serie in series:
      word= serie

    serie_page = url+word
    page = requests.get(serie_page)

    soup = bs4.BeautifulSoup(page.text,'html.parser')
    episodes = soup.select('.row2.footer')
  
    max_seas = int(episodes[0].getText()[1:3])+1
    max_epi =  int(episodes[0].getText()[4:6])+1

    

    for link in episodes:
      if episode in link.getText():
        download = link.findChildren()

        for load in download:
          file = load.get('href')
          

    if driver_path() == 'Firefox': 
        browser= webdriver.Firefox(capabilities=firefox_capabilities)
    elif driver_path() == 'Opera':
        browser =  webdriver.Opera()
    elif driver_path() == 'Chrome':
        browser = webdriver.Chrome()
    else:
        browser = webdriver.Ie()
    
  
    
   
    time.sleep(2)
    #Opens the page automatically using selenium
    browser.get(file)
    time.sleep(5)
    
    #Finds the skip_button on the page
    try:
      skip_button = browser.find_element_by_id('skip_button')
      href = skip_button.get_attribute('href')
    except selenium.common.exceptions.ElementNotVisibleException:
      messagebox.showinfo('Done', 'Please click the skip button')
      
    skip_button.click()
    time.sleep(2)
    browser.quit()
      
  except (ConnectionResetError,requests.packages.urllib3.exceptions.ProtocolError,
          requests.exceptions.ChunkedEncodingError,
          requests.exceptions.ConnectionError,ConnectionError,
          requests.packages.urllib3.exceptions.MaxRetryError,
          requests.packages.urllib3.exceptions.NewConnectionError,gaierror,AttributeError) as e:
     return 'Connection failed'     
    #
#-------------------------------------------------------------------------------------------------------------------------------------------------------

#Returns the browser type available--------------------------------------------------------------------------------------------------------
def drivers():
    if os.path.exists(r'C:\Program Files (x86)\Mozilla Firefox'):
        return 'Firefox'
    elif os.path.exists(r'C:\Program Files (x86)\Opera'):
        return 'Opera'
    elif os.path.exists(r'C:\Program Files (x86)\Google\Chrome'):
      return 'Chrome'
    else:
        return 'IE'
#-------------------------------------------------------------------------------------------------------------------------------------------------------

#Reactions-----------------------------------------------------------------------------------------------------------------------------------------

def start(*args):
  global logs
  global season1
  global serie_combo
  global get_img
  global img_src

  try:    
    serie = serie_combo.get()
      
    if serie == 'Friends':
      while check('http://o2tvseries.com/Friends/index.html') == 'Connection failed':
        check_fail = messagebox.askretrycancel('Connection Error','Connection Failed. Reconnect and try again' )    
        if check_fail == True:
          continue
        else:
          break
      else:
        tplvl = TopLevel()
        name = os.path.basename(img_src)
        if os.path.exists('imgs'):
          file = os.path.join('imgs',name)
          with open(file,'wb')as path:
              for chunks in get_img.iter_content(1000):
                  path.write(chunks)

        else:
          os.mkdir('imgs')
          file = os.path.join('imgs',name)
          with open(file,'wb')as path:
              for chunks in get_img.iter_content(1000):
                  path.write(chunks)

        pik = Image.open(file)
        tk_pik = ImageTk.PhotoImage(pik)
        label = Label(tplvl,image=tk_pik)
        label.image = tk_pik
        label.grid(row=0,column=0)
        
        lab2 = Label(tplvl,text=season1 + ': ' + check('http://o2tvseries.com/Friends/index.html'))
        lab2.grid(row=1,column=0)

        close_button = Button(tplvl,text = 'Close',command = tplvl.destroy,relief = GROOVE)
        close_button.grid(row=3,column=0)
        os.remove(file)       
    with open('series.txt','r') as serie_txt:
      url = [serie_url.strip('\n') for serie_url in serie_txt.readlines() if serie.lower() in serie_url]
      

    while check(url[0]) == 'Connection failed':
      check_fail = messagebox.askretrycancel('Connection Error','Connection Failed. Reconnect and try again' )    
      if check_fail == True:
        continue
      else:
        break
    else:
      if len(url) > 0:
        tplvl = Toplevel()
        name = os.path.basename(img_src)
        if os.path.exists('imgs'):
          file = os.path.join('imgs',name)
          with open(file,'wb') as path:
            for chunks in get_img.iter_content(1000):
                path.write(chunks)

        else:
         os.mkdir('imgs')
         file = os.path.join('imgs',name)
         with open(file,'wb')as path:
            for chunks in get_img.iter_content(1000):
                path.write(chunks)

      pik = Image.open(file)
      tk_pik = ImageTk.PhotoImage(pik)
      label = Label(tplvl,image=tk_pik)
      label.image = tk_pik
      label.grid(row=0,column=0)
      
      lab2 = Label(tplvl,text=season1 + ': ' + check(url[0]))
      lab2.grid(row=1,column=0)

      close_button = Button(tplvl,text = 'Close',command = tplvl.destroy,relief=GROOVE)
      close_button.grid(row=3,column=0)
      os.remove(file)
      
  except IndexError:
    pass
#------------------------------------------------------------------------------------------------------------------------------------------------    

#Changes tv-serie list to hd option when checkbutton is clicked-----------------------------------------------------------------------------
def checked():
  global int_var
  global serie_entry
  global lst
  global root
  global episode_entry
  global down_but
  global logs
  
  on_off = int_var.get()
  
  if on_off == 1:
    down_but.configure(command=hddownload)
    with open('today_epi.txt','r') as links:
      today_list = [link.strip('\n') for link in links.readlines()]
      today_list.sort()
      
    serie_entry['values'] = today_list[0:]
    serie_entry.current(0)

    season_entry['values'] =  ['S0{}'.format(i) if len(str(i)) == 1 else 'S{}'.format(i) for i in range(1,11)][0:]
    season_entry.current(0)
    
    episode_entry['values'] = ['E0{}'.format(i) if len(str(i)) == 1 else 'E{}'.format(i) for i in range(1,24)][0:]
    episode_entry.current(0)
  else:
    down_but.configure(command=startDownload)
    serie_entry['values'] = lst[0:]
    serie_entry.current(0)

    season_entry['values']  = ['Season-0{}'.format(i)  if len(str(i))==1 else 'season-{}'.format(i) for i in range(1,11)][0:]
    season_entry.current(0)
    
    episode_entry['values'] = ['episode-0{}'.format(i)  if len(str(i))==1 else 'episode-{}'.format(i) for i in range(1,25)][0:]
    episode_entry.current(0)
        

#--------------------------------------------------------------------------------------------------------------------------------------------

#starts the hd download----------------------------------------------------------------------------------------------------------------
def hddownload():
  global int_var
  global serie_entry
  global season_entry
  global episode_entry
  

  try:
    log = open('gslogs.txt','a')
    with open('today_epi.txt','r') as epi:
      today_list = [ep.strip('\n') for ep in epi.readlines()]
    seri = tvres()
    if '.' in seri or "'" in seri:
      seri = seri.replace('.','-')
      seri = seri.replace("'",'-')
      
    if int_var.get() == 1:    
      for series in today_list:
        if tvres() in series:
          try:
            messagebox.showinfo('Download','Your browser will be launched and your download will begin shortly. Please be patient')
            while todaySeries(series,seaS()+epiSeas()) == 'Connection failed':
              retry = messagebox.askretrycancel('Connection Error','Connection failed. Reconnect and try again')
              if retry == True:
                continue
              else:
                break
          except selenium.common.exceptions.ElementNotVisibleException:
            messagebox.showinfo('Done', 'Please click the skip button')
  except (IndexError) as wire_error:
    log.write('Wire.exe not in PATH'+'\n')
    raise IndexError()
    messagebox.showwarning('File not found', 'Please add the selenium directory to your system PATH')
  log.close()
#-------------------------------------------------------------------------------------------------------------------------------------------
  
    
#creates widgets----------------------------------------------------------------------------------------------------------------------
def label(*args):
  root,text,image,bg,fg,row,column,columnspan,sticky = args[0:]
  
  label_auto = Label(root,text=text,image=image,bg=bg,fg=fg)
  label_auto.grid(row=row,column=column,columnspan=columnspan,sticky=sticky)
  return label_auto

def buttons(*args):
  global int_var
  root,text,bg,fg,relief,command,row,column,columnspan,sticky = args[0:]

  button_auto = Button(root,text=text,bg=bg,fg=fg,relief=relief,command=command)
  button_auto.grid(row=row,column= column,columnspan=columnspan,sticky=sticky)
  return button_auto

#--------------------------------------------------------------------------------------------------------------------------------------------

#returns the values of the selected tv-serie,season,episode----------------------------------------------------------------------------------
def epiSeas(*args):
  global season_max
  global episode_entry

  return episode_entry.get()

def seaS(*args):
  global season_entry
  return season_entry.get()
  
def tvres(*args):
  return serie_entry.get()
#---------------------------------------------------------------------------------------------------------------------------------------------------




#Toggles the serie entry-------------------------------------------------------------------------------------------------------------------

def tv(*args):
  global serie_entry
  global season_entry
  global season_max
  global max_seas
  global max_epi
  
  if int_var.get() != 1:
    seri = serie_entry.get()
    
    with open('series.txt','r') as urls:
      for url in urls:
        if seri.lower() in url:
          check(url)
          
          while season_max == None:
            messageBox = messagebox.askretrycancel('Connection Error','Connection Failed. Reconnect and try again')

            if messageBox == True:
              continue
            else:
              break
          else:
            try:
              new_seasons = ['Season-0{}'.format(i) if len(str(i)) == 1 else 'Season-{}'.format(i) for i in range(1,season_max)]
            
              season_entry['values'] = new_seasons[0:]
              season_entry.current(0)
            except TypeError:
              pass
  else:
    seri = serie_entry.get().lower()
    if '.' in seri or "'" in seri:
      seri = seri.replace('.','-')
      seri = seri.replace("'",'-')
    
    with open('today.txt','r') as today:
      series = [serie_url.strip('\n') for serie_url in today.readlines() if seri in serie_url]
      try:
          
        while hdCheck(series[0]) == 'Connection failed':
          sea = messagebox.askretrycancel('Connection Error','Connection Failed. Reconnect and try again')
          if sea == True:
            continue
          else:
            break
        else:
          season_entry['values'] = ['S0{}'.format(i) if len(str(i)) == 1 else 'S{}'.format(i) for i in range(1,max_seas)][0:]
          season_entry.current(0)
      except (TypeError,IndexError) as e:
        pass

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
      

#Returns max number of seasons available--------------------------------------------------------------------------------------------------------------            

def seaClicked(*args):
  global max_epi
  global episode_entry
  global serie_entry
  global int_var

  if seaS() in the_episodes.keys():
    epi = the_episodes[seaS()][8:11]
    episode_entry['values'] = ['episode-0{}'.format(i)  if len(str(i))==1 else 'episode-{}'.format(i) for i in range(1,int(epi)+1)][0:]
    episode_entry.current(0)

  else:
    seri = serie_entry.get()
    if '.' in seri or "'" in seri:
      seri = seri.replace('.','-')
      seri = seri.replace("'",'-') 
    
    with open('today.txt','r') as today:
      series = [serie_url.strip('\n') for serie_url in today.readlines() if seri in serie_url]
      
    if len(series)==0:
      pass
    else:
      hdCheck(series[0],seaS())

    try:
      episode_entry['values'] = ['E0{}'.format(i)  if len(str(i))==1 else 'E{}'.format(i) for i in range(1,max_epi)][0:]
      episode_entry.current(0)  
    except TypeError:
      pass
  

#--------------------------------------------------------------------------------------------------------------------------------------------------------

#Starts download----------------------------------------------------------------------------------------------------------------------------
def startDownload():
  with open('series.txt','r') as urls:
    for line in urls.readlines():
      if tvres().lower() in line:
        download(line,seaS(),epiSeas())
#-------------------------------------------------------------------------------------------------------------------------------------------------------------

#Handles events-------------------------------------------------------------------------------------------------------------------------------------------------
def mouseIn(event):
  button = event.widget
  button.config(bg = 'light blue')

def mouseOut(event):
  button = event.widget
  button.config(bg = '#f3efec')
#-------------------------------------------------------------------------------------------------------------------------------------------------------
def destroy():
  global root
  close = messagebox.askyesno('Exit','Are you sure you want to exit?')
  if close == True:
    root.destroy()
  else:
    pass

def about():
  webbrowser.open('http://getserie.wordpress.com/about')
  
def grab_episodes():
  try:
      with open('url.txt','r') as page ,open('episode_new.txt','w') as file,open('series_new.txt','w') as epis,open('today_url.txt','r') as page1, open('today_new.txt','w') as today, open('today_epi_new.txt','w') as today_epi:

        url = page.readline().strip('\n')
        site = requests.get(url)
        soup = bs4.BeautifulSoup(site.text,'html.parser')
        serie = soup.select('.data a')

        links = [x.text.strip('\n').replace(' ','-') for x in serie]
        epi = [x.get('href') for x in serie]
        for link in links:
          file.write((link+'\n'))

     
        for ep in epi:
          epis.write(ep+'\n')
        hd = page1.readline()

        for j in range(0,240,12):
          shift = '?start={}'.format(j)
          tv_series = requests.get(hd +shift)
          soup1 = bs4.BeautifulSoup(tv_series.text,'html.parser')
          serie1 = soup1.select('.uk-article-title1 a')
        
          for i in serie1:
            today.write(i.get('href') + '\n')
            name = i.getText()
            name = name.replace(' ','-')
            today_epi.write(name+'\n')
     
      messagebox.showinfo('Done', 'Series list updated')
      
  except (ConnectionResetError,requests.packages.urllib3.exceptions.ProtocolError,
          requests.exceptions.ChunkedEncodingError,
          requests.exceptions.ConnectionError,ConnectionError,
          requests.packages.urllib3.exceptions.MaxRetryError,
          requests.packages.urllib3.exceptions.NewConnectionError,gaierror) as e:

    files = ['episode_new.txt',
           'series_new.txt',
           'today_new.txt',
           'today_epi_new.txt']
    for txts in files:
      os.remove(txts)

    return 'Connection Failed'

def update_list():
  while grab_episodes() == 'Connection Failed':
    retry = messagebox.askretrycancel('Connection Error','Connection Failed. Reconnect and try again')
    if retry == True:
      continue
    else:
      break
  else:
    
    with open('today_epi.txt','w') as t_epi, open('today.txt','w') as today, open('episodes.txt','w') as epi, open('series.txt','w') as series, open('episode_new.txt','r') as file, open('series_new.txt','r') as epis, open('today_new.txt','r') as today1, open('today_epi_new.txt','r') as today_epi_n:
      for lines in today_epi_n.readlines():

        if ':-' in lines or "'" in lines:
          lines = lines.replace(':-','-')
          lines = lines.replace("'",'-')
          t_epi.write(lines.lower())

        elif '.-' in lines :
          lines = lines.replace('.-','-')
          t_epi.write(lines.lower())

        elif '.' in lines:
          lines = lines.replace('.','-')
          t_epi.write(lines.lower())

        else:
          t_epi.write(lines.lower())
          

      for t_lines in today1.readlines():
        today.write(t_lines.lower())

      for f_lines in file.readlines():
        epi.write(f_lines.lower())

      for e_lines in epis.readlines():
        series.write(e_lines.lower())
            

    files = ['episode_new.txt',
           'series_new.txt',
           'today_new.txt',
           'today_epi_new.txt']
    for txts in files:
      os.remove(txts)

def update():
  messagebox.showinfo('Done','No updates available')
  
#Creates GUI------------------------------------------------------------------------------------------------------------------------------------------------
def main():
  global serie_combo
  global int_var
  global serie_entry
  global lst
  global root
  global season_entry
  global episode_entry
  global down_but
  
  root = Tk()

  root.rowconfigure(0,weight=1)
  root.columnconfigure(0,weight=1)
      
  root.rowconfigure(1,weight=1)
  root.columnconfigure(1,weight=1)

  root.rowconfigure(2)
  root.columnconfigure(2,weight=2)

  root.rowconfigure(3,weight=1)
  root.columnconfigure(3,weight=1)

  root.rowconfigure(4,weight=1)
  root.columnconfigure(4,weight=1)

  root.rowconfigure(4,weight=1)
  root.columnconfigure(1,weight=1)

  root.rowconfigure(5,weight=1)
  root.columnconfigure(5,weight=1)
  
  root.rowconfigure(6,weight=1)
  
  root.rowconfigure(7,weight=1)

  logo = PhotoImage(file='getseries.gif')
  label(root,None,logo,None,None,1,0,6,'nsew')

  label(root,'Enter serie name to check for latest episodes',None,'#f3efec','black',2,0,5,'nsew')

  label(root,'Serie',None,'#f3efec','black',3,0,None,None)

  label(root,'',None,'#f3efec','#f3efec',5,1,4,None)

  label(root,'Enter serie name, season and episode to download',None,'#f3efec','black',6,0,5,None)

  label(root,'Season',None,'#f3efec','black',8,2,None,None)

  label(root,'Tv-serie',None,'#f3efec','black',8,0,None,None)

  label(root,' ',None,'#f3efec',None,8,5,None,None)

  label(root,' ',None,'#f3efec',None,10,0,None,None)
  
  label(root,'Episode',None,'#f3efec','black',8,4,None,None)
  
  check_but = buttons(root,'Check','#f3efec','black',GROOVE,start,4,1,5,None)
  check_but.bind('<Enter>',mouseIn)
  check_but.bind('<Leave>',mouseOut)
  
  down_but = buttons(root,'Download','#f3efec','black',GROOVE,startDownload,9,1,5,None)
  down_but.bind('<Enter>',mouseIn)
  down_but.bind('<Leave>',mouseOut)
  
  menu = Menu(root)
  filemenu = Menu(menu)
  filemenu.add_command(label='Open')
  filemenu.add_command(label='Exit',command=destroy)

  helpmenu = Menu(menu)
  helpmenu.add_command(label='Update series list', command=update_list)
  helpmenu.add_command(label='About getSERIES',command=about)
  helpmenu.add_command(label='Check for updates',command=update)

  menu.add_cascade(label='File',menu=filemenu)
  menu.add_cascade(label='Help',menu=helpmenu)
  with open('episode.txt','r') as epi:
      lst = [line.strip('\n') for line in epi.readlines()]
      lst.sort()
      
  str_var1 = StringVar()
  serie_combo= ttk.Combobox(root,textvariable=str_var1)
  serie_combo['values'] = (lst[0:])
  serie_combo.current(0)    
  serie_combo.grid(row=3,column=1,columnspan=4,sticky='nsew')
  #serie_combo.xview_scroll

  str_var2 = StringVar()
  serie_entry = ttk.Combobox(root,textvariable=str_var2)
  serie_entry['values'] = lst[0:]
  serie_entry.current(0)
  serie_entry.bind('<<ComboboxSelected>>',func=tv)
  serie_entry.grid(row=8,column=1)

  int_var = IntVar()
  hd_check = Checkbutton(root,text='HD',relief=FLAT,bg='#f3efec',fg='black',command=checked,variable=int_var)
  hd_check.grid(row=7,column=0)

  str_var4 = StringVar()
  season_entry = ttk.Combobox(root,textvariable=str_var4)
  seasons = ['Season-0{}'.format(i)  if len(str(i))==1 else 'season-{}'.format(i) for i in range(1,11)]
  season_entry['values'] = seasons[0:]
  season_entry.current(0)
  season_entry.bind('<<ComboboxSelected>>',func=seaClicked)
  season_entry.grid(row=8,column=3)

  str_var3 = StringVar()
  episode_entry = ttk.Combobox(root,textvariable=str_var3)
  episodes = ['episode-0{}'.format(i)  if len(str(i))==1 else 'episode-{}'.format(i) for i in range(1,25)]
  episode_entry['values'] = episodes[0:]
  episode_entry.current(0)
  episode_entry.bind('<<ComboboxSelected>>',func=epiSeas)
  episode_entry.grid(row=8,column=5)  
   
  root.configure(background='#f3efec')
  root.geometry('600x260')
  root.iconbitmap(default='ti.ico')
  root.title('getSERIES')
  root.wm_resizable(False,False)
  root.config(menu=menu)

  root.mainloop()
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  
main()
