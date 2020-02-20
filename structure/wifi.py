import network
import socket

def check_credentials():
  global cred_ssid, cred_psw
  file = open("/structure/credentials","r")
  data = file.read()
  file.close()

  cred_ssid=data.split(",")[0]
  cred_psw=data.split(",")[1]
  
  if cred_ssid == 'null':
    return False,cred_ssid,cred_psw
  else:
    return True,cred_ssid,cred_psw
    
    
def get_credentials():
  print('Get Wifi Credentials')
  station = network.WLAN(network.STA_IF) 
  station.active(True)
  html = create_html(station.scan())
  start_web_server(html)


def set_credentials(c_data):
  print('Got credentials: ', c_data)
  print('Saving credentials...')
  file = open("/structure/credentials","w")
  file.write(c_data)
  file.close()
  print('restarting machine...')
  import machine
  machine.reset()
  

def create_html(scan_list):
  tr_swap=""
  tr_format="""
  <tr>
    <td onclick="set_ssid(this)">$ssid</td>
    <td class=$signal_state style="width:120px">$signal_state</td>
  </tr>
  """

  for wifi_net in scan_list:
    net_signal=int(str(wifi_net[3]).replace('-',''))
    net_ssid=str(wifi_net[0]).replace("b'",'')
    net_ssid=net_ssid.replace("'",'')
    signal_state=''
    if net_signal <= 66:
      signal_state = "Excelente"

    if net_signal >= 67:
      signal_state = "Buena"
      
    if net_signal >= 80:
      signal_state = "Mala"
      
    tr_done = tr_format.replace('$ssid',net_ssid).replace('$signal_state',signal_state)
    tr_swap = tr_swap + tr_done

  print(tr_swap)
  file = open('/structure/get_wifi.html','r')
  html = file.read()
  html = html.replace('$tr_swap',tr_swap).replace('$cred_ssid',cred_ssid).replace('$cred_psw',cred_psw)
  file.close()
  return html


def start_web_server(html):
  try:
    port=80
    ap_wlan = network.WLAN(network.AP_IF)
    ap_wlan.active(True)
    ap_wlan.config(essid='delec_ESP32')
    ap_wlan.config(authmode=3, password='12551255')

    print('Access point created')
    print('AP Network data: ',ap_wlan.ifconfig())

    ap_localhost=ap_wlan.ifconfig()[0]            #get ip addr

    print('Got IP')
    ap_socket = socket.socket()                   #create socket
    print('Socket created')
    ap_socket.bind((ap_localhost,port))           #bind ip and port
    print('Socket bind complete')
    ap_socket.listen(1)                           #listen message
    print('Socket now listening')                 
    print('Listening port:',port)
    
    #Set the value of the given socket option
    ap_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    while True:
      client, address = ap_socket.accept()
      ip, port = str(address[0]), str(address[1])
      print('connection from ' + ip + ':' + port)
      client_file = client.makefile('rwb', 0)
      
      while True:
        line = client_file.readline()
        data = str(line).replace("b'",'').replace("'",'')
        print(data)
        if not line or line == b'\r\n':
          break
        #"b'GET /?@ssid:TP-LINK_56A8@ssid_psw:1234oooooo HTTP/1.1\r\n'"
        get_credentials = data.find('@credentials:')
        end_data = data.find('@end')
        
        if get_credentials != -1:
          print('Found credentials')
          c_data = data[get_credentials+len('@credentials:'): end_data]
          set_credentials(c_data)

      response = html
      client.send(response)
      client.close()
  except:
    if(ap_socket):
      ap_socket.close()
    ap_wlan.disconnect()
    ap_wlan.active(False)
    print('ap_closed')


def connect(cred_ssid,cred_psw):
  print('\n{\n\tConnecting to network: ' +cred_ssid)
  st_wlan = network.WLAN(network.STA_IF)
  st_wlan.active(True)
  
  if cred_ssid != 'null':
    if not st_wlan.isconnected():
      st_wlan.connect(cred_ssid,cred_psw)
      while not st_wlan.isconnected():
        pass
      print('\tConnected, st_wlan:', st_wlan.ifconfig(), '\n}\n')
      return True
    else:
      print('\tAlready connected to:', cred_ssid, '\n\t', st_wlan.ifconfig(),'\n}\n')
      return True
  else:
    try:
      print('\n{\n\treconnecting to network: ' +cred_ssid)
      if not st_wlan.isconnected():
        st_wlan.connect()
        while not st_wlan.isconnected():
          pass
        print('\tConnected, st_wlan:', st_wlan.ifconfig(), '\n}\n')
        return True
      else:
        print('\tAlready connected to:', st_wlan.ifconfig(), '\n}\n')
        return True
    except:
      print('failed to reconnect')
      print('get wifi credentials')
      return False
      
      