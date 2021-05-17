from __future__ import print_function
import os


def is_secured(wifi):
    wifi = wifi.split(":")[1]
    return wifi != ""


def get_wifi_list():
    # wifi_list = os.popen('nmcli d wifi list').read()
    wifi = os.popen('nmcli -f SSID -t device wifi list').read()
    signal = os.popen('nmcli -f BARS -t device wifi list').read()
    security = os.popen('nmcli -f SECURITY -t device wifi list').read()
    wifi_list = (wifi.split('\n'))
    signal_list = (signal.split('\n'))
    security_list = (security.split('\n'))
    return wifi_list, signal_list, security_list


def know_wifi_list():
    command = 'nmcli -f name,type con'
    return_code = os.popen(command).read()
    list_wifi_type = return_code.split('\n')
    wifi_list = [wifi.split('wifi')[0].strip()
                 for wifi in list_wifi_type if 'wifi' in wifi]
    return wifi_list


def delete_wifi(wifi):
    command = 'nmcli connection delete ' + wifi
    return os.popen(command).read()


def check_exist_wifi():
    command = 'nmcli -f name con'
    return os.popen(command).read().split('\n')


def disconnect(wifi):
    command = 'nmcli con down id ' + wifi
    return os.popen(command).read()


def is_connect_with_old_wifi():
    cmd = 'nmcli -f GENERAL.CONNECTION dev show wlan0'
    old_wifi = os.popen(cmd).read().split('GENERAL.CONNECTION:')[1].strip()
    if (old_wifi != '--'):
        cmd = 'nmcli con down id ' + old_wifi
        os.popen(cmd).read()


def name_know_wifi_list(wifi):
    command = 'nmcli -f name con'
    return_code = os.popen(command).read()
    list_wifi = return_code.split('\n')
    list_wifi = [wifi.strip() for wifi in list_wifi]
    return list_wifi


def connect_old_wifi(wifi):
    command = 'nmcli con up ' + wifi
    return os.popen(command).read()


def get_ip_from_wifi_connected():
    return os.popen('nmcli -f IP4.ADDRESS dev show wlan0').read().split('IP4.ADDRESS[1]:')[1].strip()


def get_ip_from_eth0():
    try:
        return os.popen('nmcli -f IP4.ADDRESS dev show eth0').read().split('IP4.ADDRESS[1]:')[1].split('/')[0].strip()
    except:
        return ''


def connect_new_wifi(wifi, pwd):
    if (pwd == ''):
        command = 'nmcli device wifi connect ' + wifi
    else:
        command = 'nmcli device wifi connect ' + wifi + ' password ' + pwd
    return os.popen(command).read()


def disable_eth0():
    command = 'sudo ifconfig eth0 down'
    return os.popen(command).read()


def re_enable_eth0():
    command = 'sudo ifconfig eth0 up'
    return os.popen(command).read()


def set_eth0_default():
    command = 'sudo ip route del default dev wlan0'
    os.popen(command).read()
    command = 'sudo ip route add default dev eth0'
    return os.popen(command).read()


def set_wlan0_default():
    command = 'sudo ip route del default dev eth0'
    os.popen(command).read()
    command = 'sudo ip route add default dev wlan0'
    return os.popen(command).read()


def is_eth0():
    command = 'nmcli -f WIRED-PROPERTIES.CARRIER dev show eth0'
    wired = os.popen(command).read()
    command = 'nmcli -f GENERAL.STATE dev show eth0'
    state = os.popen(command).read()
    command = 'nmcli -f IP4.ADDRESS dev show eth0'
    ip_addr = os.popen(command).read()
    if (wired.find('off') != -1):
        return False
    elif (state.find('20') != -1 or state.find('30') != -1):
        return False
    elif (ip_addr.find('169.254') != -1):
        return False
    else:
        return True


def is_wifi_support():
    command = 'nmcli dev show wlan0'
    res = os.popen(command).read()
    if (res.find("'wlan0' not found") != -1):
        return False
    else:
        return True


def main():
    while(1):
        command = input("Please type: ")
        return_code = os.popen(command).read()
        print(return_code)


if __name__ == '__main__':
    main()
