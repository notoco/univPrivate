# -*- coding: utf-8 -*-
import control

info = ''
state = control.get_setting('state')

if __name__ == '__main__':
    arg = None

    try:
       arg = sys.argv[1].lower()
    except Exception:
       pass

    if arg == "on":
        control.turn_on()
        control.set_setting('state', 'true')
        info = 'ON'
    elif arg == "off":
        control.turn_off()
        control.set_setting('state', 'false')
        info = 'OFF'
    elif arg == "switch":
        if state == 'true':
            control.turn_off()
            control.set_setting('state', 'false')
            info = 'OFF'
        else:
            control.turn_on()
            control.set_setting('state', 'true')
            info = 'ON'    
        
    control.send_notification(info)
