# -*- coding: utf-8 -*-
# post_data.py

# read post data
def data(fn):
    # dictionary
    Post = { \
        'iter'       : 0,               \
        'p1dcompo'   : [],              \
        'p1ddir'     : [],              \
        'p1dpos'     : [],              \
        'p1ddb'      : 0,               \
        'p1dscale'   : [0, 0, 0, 0],    \
        'p1dlog'     : 0,               \
        'p2dcompo'   : [],              \
        'p2ddir'     : [],              \
        'p2dpos'     : [],              \
        'p2dfigure'  : [0, 0],          \
        'p2ddb'      : 0,               \
        'p2dscale'   : [0, 0, 0, 20],   \
        'p2dcontour' : 0,               \
        'p2dobject'  : [1, 1, 1],       \
        'p2dzoom'    : [0, 0, 0, 0, 0], \
        'p2dlog'     : 0}

    # read file
    with open(fn, 'rt', encoding='utf-8') as fp:
        header = fp.readline()
        lines = fp.readlines()

    # header
    d = header.strip().split()
    if (len(d) < 3) or (d[0] != 'OpenSTF'):
        print('*** Not OpenSTF data : %s' % fn)
        return
    version = (100 * int(d[1])) + int(d[2])
    if version < 301:
        print('*** version of data is old : %s.%s < 3.1' % (d[1], d[2]))
        return

    # body
    for tline in lines:
        # token
        d = tline.strip().split()  #;print(d)
        
        # check
        if d[0].startswith('#'):
            continue
        elif (d[0] == 'end'):
            break
        elif (len(d) < 3):
            continue
        elif (d[1] != "="):
            continue

        # parameter array
        p = d[2:]  #;print(p)
        
        # input
        key = d[0]
        if   key == 'plotiter':
            Post['iter'] = int(p[0])
        elif key == 'plot1d':
            if len(p) > 3:
                #n1d = n1d + 1;
                if not p[0] in ['V', 'E', 'D', 'Q']:
                    print('*** invalid component : ' + p[0])
                    continue
                if not p[1] in ['X', 'Y', 'Z']:
                    print('*** invalid direction : ' + p[1])
                    continue
                Post['p1dcompo'].append(p[0])
                Post['p1ddir'].append(p[1])
                Post['p1dpos'].append([float(p[2]), float(p[3])])
        elif key == '1ddb':
            #Post['p1ddb'] = int(p[0])
            Post['p1ddb'] = 1 if p[0] == '1' else 0
        elif key == '1dscale':
            Post['p1dscale'][0] = 1
            if len(p) > 2:
                Post['p1dscale'][1] = min(float(p[0]), float(p[1]))
                Post['p1dscale'][2] = max(float(p[0]), float(p[1]))
                Post['p1dscale'][3] = max(int(p[2]), 1)
        elif key == '1dlog':
            Post['p1dlog'] =  1 if p[0] == '1' else 0
        elif key == 'plot2d':
            if len(p) > 2:
                if not p[0] in ['V', 'E', 'D', 'Q']:
                    print('*** invalid component : ' + p[0])
                    continue
                if not p[1] in ['X', 'Y', 'Z']:
                    print('*** invalid direction : ' + p[1])
                    continue
                #n2d = n2d + 1;
                Post['p2dcompo'].append(p[0])
                Post['p2ddir'].append(p[1])
                Post['p2dpos'].append(float(p[2]))
        elif key == '2dfigure':
            if len(p) > 1:
                Post['p2dfigure'] = [int(p[0]), int(p[1])]  # not used
        elif key == '2ddb':
            Post['p2ddb'] = 1 if p[0] == '1' else 0
        elif key == '2dscale':
            Post['p2dscale'][0] = 1
            if len(p) > 2:
                Post['p2dscale'][1] = min(float(p[0]), float(p[1]))
                Post['p2dscale'][2] = max(float(p[0]), float(p[1]))
                Post['p2dscale'][3] = max(int(p[2]), 1)
        elif key == '2dcontour':
            Post['p2dcontour'] = int(p[0])
        elif key == '2dobject':
            Post['p2dobject'][0] = 1
            if len(p) > 1:
                Post['p2dobject'][1:3] = [int(p[0]), int(p[1])]
        elif key == '2dzoom':
            Post['p2dzoom'][0] = 1
            if len(p) > 3:
                Post['p2dzoom'][1] = min(float(p[0]), float(p[1]))
                Post['p2dzoom'][2] = max(float(p[0]), float(p[1]))
                Post['p2dzoom'][3] = min(float(p[2]), float(p[3]))
                Post['p2dzoom'][4] = max(float(p[2]), float(p[3]))
        elif key == '2dlog':
            Post['p2dlog'] = 1 if p[0] == '1' else 0

    return Post
