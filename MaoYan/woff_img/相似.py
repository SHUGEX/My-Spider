from fontTools.ttLib import TTFont


def compare(AA, BB):
    # print(f"\naa {len(AA)}\n", AA,f"\nbb {len(BB)}\n", BB)
    # print(f"\naa {len(AA)}\n", f"\nbb {len(BB)}\n")
    # if abs(len(AA) - len(BB))<3:
    #     return True
    # else:
    #     return False
    # for i in range(min(len(AA),len(BB))):
    #     if abs(AA[i][0] - BB[i][0]) < 300 and abs(AA[i][1] - BB[i][1]) < 300:
    #         pass
    #     else:
    #         return False
    # return True

    for i in range(4):
        if (abs(AA[i][0] - BB[i][0]) < 100) and (abs(AA[i][1] - BB[i][1]) < 100):
            pass
        else:
            return False
    return True


def modify_html(newFont):
    basefont = TTFont('227e3c01/227e3c01.woff')
    unilist = newFont['cmap'].tables[0].ttFont.getGlyphOrder()[2:]
    print(unilist)
    numlist = []
    base_num = ['1', '9', '0', '2', '5', '8', '7', '3', '4', '6']
    base_unicode = ['uniE51E', 'uniE70D', 'uniE633', 'uniECB1', 'uniF0AD',
                    'uniF4B3', 'uniF8A4', 'uniF014', 'uniF76B', 'uniF509']
    for i in range(1, len(unilist)):
        newGlyph = newFont['glyf'][unilist[i]].coordinates
        for j in range(len(base_unicode)):
            baseGlyph = basefont['glyf'][base_unicode[j]].coordinates

            if compare(newGlyph, baseGlyph):
                numlist.append(base_num[j])
                break
    rowList = []
    for i in unilist:
        i = i.replace('uni', '').lower()
        rowList.append(i)
    print(rowList, numlist)
    dictory = dict(zip(rowList, numlist))
    return dictory

newFont = TTFont('eb54399b/eb54399b.woff')
modify_html(newFont)