#!/usr/bin/env python3

from xml.etree import ElementTree as ET
import re

def ParseAshx(ifile, ofile):
    
    x = ET.parse(ifile).getroot()
    sec = x[1][0]

    if sec.get('class') != 'Section1':
        exit

    def addChild(parent, tag, attrs = None):
        elem = ET.Element(tag)
        if attrs != None:
            for key in attrs:
                if attrs[key] != None:
                    elem.set(key, attrs[key])
        parent.append(elem)
        return elem


    doc = ET.Element("document")
    info = ET.Element("docinfo")
    changes = ET.Element("changes")
    text = ET.Element("text")

    doc.append(info)
    doc.append(text)
    info.append(changes)

    curr_razdel = None
    curr_article = None
    curr_chapter = None

    article_title = re.compile("^Статья[ |"+ chr(0xa0) +"]\d+[\.|/]\s*(\d+\.\s*)*") #После Статья идут пробел и символ \xa0

    ch_id = 0

    for i in sec.iter():
        tag = i.get('class')
        if tag == "titlek" or tag == "title": #Название
            if i.text.strip() == "": #Особый случай для банковского кодекса
                _title = ""
                for _i in i.iter():
                    if _i.tag == "span":
                        if _i.get('class') in ["name", "promulgator"]:
                            _title += _i.text
                            
                addChild(info, 'info', {'class':'title', 'text':_title})
            else:
                addChild(info, 'info', {'class':'title', 'text':i.text})
        elif tag == "datepr": #Дата принятия
            addChild(info, 'info', {'class':'date', 'text':i.text})
        elif tag == "number": #Номер документа
            addChild(info, 'info', {'class':'number', 'text':i.text})
        elif tag == "prinodobren": #Принят и одобрен
            addChild(info, 'info', {'class':'getpower', 'text':i.text})
        elif tag == "changeutrs": #Утратил силу
            addChild(info, 'info', {'class':'lostpower', 'text':i.text})
        elif tag == "changeadd": #Добавлено изменение или дополнение
            ch_id += 1
            addChild(changes, 'info', {'class':'changes', 'text':i.text, 'id':str(ch_id)})
        elif tag == "zagrazdel": #Раздел
            curr_chapter = None
            if i.get('id') != None:
                curr_razdel = addChild(text, 'razdel', {'id':i.get('id'), 'text':i.text})
        elif tag == "chapter": #Глава
            if curr_razdel == None:
                curr_razdel = text
            curr_chapter = addChild(curr_razdel, 'chapter', {'id':i.get('id'), 'text':i.text})
        elif tag in ["article", "articleintext"]: #Статья
            a_text = i.text
            if (article_title.match(i.text) != None):
                _, _, a_text = article_title.split(i.text)                
            if curr_chapter != None:
                curr_article = addChild(curr_chapter, 'article', {'id':i.get('id'), 'text':a_text})
            elif curr_razdel != None:
                curr_article = addChild(curr_razdel, 'article', {'id':i.get('id'), 'text':a_text})
           
        elif tag in ["newncpi", "contenttext"]: 
            if curr_article != None:
                if i.text != None:
                    if i.text.strip() != "":
                        addChild(curr_article, 'p', {'text':i.text})
                    
        elif tag == "point":
            if curr_article != None:
                if i.text != None:
                    if i.text.strip() != "":
                        addChild(curr_article, 'p', {'id':i.get('id'), 'text':i.text, 'class':'point'})

        elif tag == "underpoint":
            if curr_article != None:
                if i.text != None:
                    if i.text.strip() != "":
                        addChild(curr_article, 'p', {'id':i.get('id'), 'text':i.text, 'class':'underpoint'})
   
        elif tag == "comment":
             if curr_article != None:
                 if i.text != None:
                     if i.text.strip() != "":
                         addChild(curr_article, 'p', {'id':i.get('id'), 'text':i.text, 'class':'comment'})

        elif tag == "snoski":
             if curr_article != None:
                 if i.text != None:
                     if i.text.strip() != "":
                         addChild(curr_article, 'p', {'id':i.get('id'), 'text':i.text, 'class':'snoski'})

        elif tag == "rekviziti":
             if i.text != None:
                 if curr_article != None:
                     if i.text.startswith("_") and i.text.endswith("_"):
                         addChild(curr_article, 'p', {'id':i.get('id'), 'text':i.text, 'class':'rekvizit'})

        elif tag == "titlep":
            #TODO: Приложение к кодексу
            pass

        
        else:
            if not tag in ["snoskiv", None, "snoskiline",
                           "contentword", "part", "articlec", "newncpi2",
                           "Section1", "changei", "post", "pers", "preamble",
                           "promulgator", "newncpi0", "name", "append1",
                           "paragraph", "podrazdel", "numheader", "nonumheader", #образуют слишком большую вложенность
                           "table10", #Таблицы в особой части налогового кодекса
                           ]:
                pass
            


    tree = ET.ElementTree(doc)
    tmpFile = '/tmp/tmp_xml.xml'
    try:
        tree.write(tmpFile, encoding="utf-8", xml_declaration=True)

        command = 'xmllint -format -recover "%s" > "%s"'
        os.system(command % (tmpFile, ofile))
    except:
        ET.dump(doc)
        


import sys
import os
from os.path import isfile, exists, realpath, splitext
import hashlib
import time


action = None
infile = ""
ofile = ""
source_dir = 'laws_ashx'
parsed_dir = 'laws_xml'

if len(sys.argv) > 1:
    if sys.argv[1] == "--all":
        action = "all"
    elif sys.argv[1] == "--make-links":
        action = "make_links"
    elif sys.argv[1] == "--make-zlib":
        action = "make_zlib"
        file = sys.argv[2]
        print(file)
    else:
        infile = sys.argv[1]
        outfile = sys.argv[2]




if action == "all":
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            print(file)
            ParseAshx(source_dir + "/" + file, parsed_dir + "/" + file)
            
elif action == "make_zlib":
    import zlib
    files_attrib = []
    _tmp = {}
    fname = parsed_dir+"/"+file
    file_stat = os.stat(fname) #File size
    data = open(fname, 'rb').read()
    zipped = zlib.compress(data)

    files_attrib.append(_tmp)
    

    _root = ET.parse(fname).getroot()
    for i in _root.iter():
        if i.tag == "info":
            if i.get('class') == 'title':
                file_title = i.get('text').strip()

    
    _tmp["size"]  = str(file_stat.st_size)
    _tmp["packed"] = str(len(zipped))
    _tmp["name"]  = file + ".zlib"
    creationTime = int(time.time())
    _tmp["date"]  = str(creationTime)
    _tmp["title"] = file_title.title().replace("Республики Беларусь","")\
                                      .replace("  ", " ")\
                                      .replace("*|", "")\
                                      .strip()




    


    zlibFile = open('laws_zlib/' + file + ".zlib", 'wb')


    VERSION = 1
    zlibFile.write(VERSION.to_bytes(2, "little")) #Записываем первые 2 байта - версия архива
                
    OFFSET_POS = zlibFile.tell()
    zlibFile.write(b"\x00" * 4) #Резервируем для ссылки на блок упакованного файла, перед ним 4 байта длина оригинальных данных
    
    bTitle = _tmp["title"].encode()
    bTitleSize = len(bTitle).to_bytes(2, "little")
    zlibFile.write(bTitleSize) #Пишем длину имени кодекса
    zlibFile.write(bTitle) #Пишем имя кодекса

    bTime = creationTime.to_bytes(8, 'little')
    zlibFile.write(bTime) #Записываем время создания
    
    __fileName, ext = splitext(file)
    icon_name = "codex_icons/"+__fileName+".png"
    if exists(icon_name):
        picture = open(icon_name, 'rb').read()
        zlibFile.write(len(picture).to_bytes(4, 'little'))
        zlibFile.write(picture)
    else:
        zlibFile.write(b"\x00" * 4) #Если иконки нет, 4-байтный ноль

    offset = zlibFile.tell()
    zlibFile.write(file_stat.st_size.to_bytes(4, 'little'))
    zlibFile.write(zipped)
    zlibFile.seek(OFFSET_POS)
    zlibFile.write(offset.to_bytes(4, 'little'))
            

elif action == "make_links":
            
    links = ET.Element('links')
    links.set("URL", "https://github.com/aniterum/CodexesBY/raw/master/laws_zlib/")

    files_attrib = []
    

    for root, dirs, files in os.walk(parsed_dir):
        for file in files:
            _tmp = {}
            files_attrib.append(_tmp)
            fname = parsed_dir+"/"+file
            file_stat = os.stat(fname) #File size

            zipped = open('laws_zlib/' + file + ".zlib", 'rb').read()

            _root = ET.parse(fname).getroot()
            for i in _root.iter():
                if i.tag == "info":
                    if i.get('class') == 'title':
                        file_title = i.get('text').strip()

            
            _tmp["size"]  = str(file_stat.st_size)
            _tmp["packed"] = str(len(zipped))
            _tmp["name"]  = file + ".zlib"
            creationTime = int(file_stat.st_mtime)
            _tmp["date"]  = str(creationTime)
            _tmp["title"] = file_title.title().replace("Республики Беларусь","")\
                                              .replace("  ", " ")\
                                              .replace("*|", "")\
                                              .strip()

            

    for i in files_attrib:
        codex_info = ET.Element('codex')
        links.append(codex_info)
        codex_info.attrib = i
            
    tree = ET.ElementTree(links)
    tmpFile = '/tmp/tmp_xml.xml'
    try:
        tree.write(tmpFile, encoding="utf-8", xml_declaration=True)

        command = 'xmllint -format  "%s" > "%s"'
        os.system(command % (tmpFile, 'links.xml'))
    except:
        ET.dump(links)
        

else:
    if exists(infile):
        print(infile)
        ParseAshx(infile, outfile)



