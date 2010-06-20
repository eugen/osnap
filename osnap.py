#!/usr/bin/python

import sys
import sqlite3
import gtk
import wnck

db = sqlite3.connect('osnap.db')
try:
    db.execute("create table windows(id ulong, snapx int, snapy int, offsetx int, offsety int, width int, height int)")
except:
    print("table already created")
    pass

SNAPPED_NONE   = 0
SNAPPED_LEFT   = 1 << 0
SNAPPED_RIGHT  = 1 << 1
SNAPPED_TOP    = 1 << 2
SNAPPED_BOTTOM = 1 << 3

SNAPPED_HORIZ = SNAPPED_LEFT | SNAPPED_RIGHT
SNAPPED_VERT = SNAPPED_TOP | SNAPPED_BOTTOM


def get_window_state(wnd):
    row = db.execute(
         "select snapx, snapy, offsetx, offsety, width, height "+
         "from [windows] where id = $1", 
         [wnd.get_xid()]).fetchone()

    if(row != None):
        snapx, snapy, x, y, w, h = row
        return ((snapx, snapy), x, y, w, h)
    else:
        x, y, w, h = wnd.get_geometry()
        return ((0, 0), x, y, w, h)

def set_window_state(wnd, state, geometry):
    x, y, w, h = geometry
    snapx, snapy = state
    xid = wnd.get_xid()
    db.execute("delete from [windows] where id = $1", [xid])
    db.execute("insert into [windows] values($1, $2, $3, $4, $5, $6, $7)",
                 [xid, snapx, snapy, x, y, w, h])

def toggle_snap(snapx, snapy):
    scr = wnck.screen_get_default()
    # pending gtk events must be treated before any windows can be investigated
    while gtk.events_pending():
        gtk.main_iteration()
    wnd = scr.get_active_window()
    if(not(wnd)):
        print("cannot get active window!")
        return

    (oldsnapx, oldsnapy), oldx, oldy, oldwidth, oldheight = get_window_state(wnd)

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

try:
    toggle_snap(int(sys.argv[1]), int(sys.argv[2]))
finally:
    db.commit()
    db.close()
