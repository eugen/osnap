#!/usr/bin/python

from datetime import datetime
import gtk
import wnck
import keybinder

window_states = {}

def get_window_state(wnd):
    xid = wnd.get_xid()
    if(window_states.has_key(xid)):
        return window_states[xid]
    else:
        x, y, w, h = wnd.get_geometry()
        return ((0, 0), (x, y, w, h))

def set_window_state(wnd, state, geometry):
    xid = wnd.get_xid()
    window_states[xid] = (state, geometry)

def toggle_snap(snapx, snapy):
    scr = wnck.screen_get_default()
    # pending gtk events must be treated before any windows can be investigated
    while gtk.events_pending():
        gtk.main_iteration()
    wnd = scr.get_active_window()
    if(not(wnd)):
        print("cannot get active window!")
        return

    (oldsnapx, oldsnapy), (oldx, oldy, oldwidth, oldheight) = get_window_state(wnd)

    if((oldsnapx, oldsnapy) == (0, 0)):
        # if unsnapped, get the unmaximized (i.e. normal) geometry
        if(wnd.is_maximized()):
            wnd.unmaximize()
        (oldx, oldy, oldwidth, oldheight) = wnd.get_geometry()
    
    if(oldsnapx == snapx):
        snapx = 0
    else:
        snapx = snapx or oldsnapx

    if(oldsnapy == snapy):
        snapy = 0
    else:
        snapy = snapy or oldsnapy

    width = oldwidth
    if snapx:
        width = scr.get_width() / 2

    height = oldheight
    if snapy: 
        height = scr.get_height() / 2
    
    x = oldx;
    if(snapx == -1):
        x = 0
    elif(snapx == 1):
        x = scr.get_width() / 2
    
    y = oldy
    if(snapy == -1):
        y = 0
    elif(snapy == 1):
        y = scr.get_height() / 2

    if(oldsnapx and not(snapx) or snapy):
        wnd.unmaximize_vertically()
    if(oldsnapy and not(snapy) or snapx):
        wnd.unmaximize_horizontally()

    if(snapx and not(snapy)):
        wnd.maximize_vertically()
    if(snapy and not(snapx)):
        wnd.maximize_horizontally()

    wnd.set_geometry(10, 15, x, y, width, height)

    set_window_state(wnd, (snapx, snapy), (oldx, oldy, oldwidth, oldheight))



def osnap_h(data):
    [snapx, snapy] = [int(x) for x in data.split(',')]
    toggle_snap(snapx, snapy)

def bind_shortcuts():
    keybinder.bind("<Super>Left", osnap_h, "-1,0");
    keybinder.bind("<Super>Right", osnap_h, "1,0");
    keybinder.bind("<Super>Up", osnap_h, "0,-1");
    keybinder.bind("<Super>Down", osnap_h, "0,1");

bind_shortcuts();
gtk.main()
