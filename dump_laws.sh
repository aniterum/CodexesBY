#!/bin/bash

IFS=$(echo -en "\n\b")

DATA="constitution|v19402875|Конституция
contr_corruption|H11500305|О борьбе с коррупцией
bank|HK0000441|Банковский кодекс
budget|Hk0800412|Бюджетный кодекс
water|HK9800191|Водный кодекс
air|Hk0600117|Воздушный кодекс
civil|HK9800218|Гражданский кодекс
civil_proc|HK9900238|Гражданский процессуальный кодекс
housing|Hk1200428|Жилищный кодекс
voting|HK0000370|Избирательный кодекс
vater_transport|Hk0200118|Кодекс внутреннего водного транспорта
marriage_family|HK9900278|Кодекс о браке и семье
ground|Hk0800425|Кодекс о земле
underground|Hk0800406|Кодекс о недрах
court_and_judge|Hk0600139|Кодекс о судоустройстве и статусе судей
admin|Hk0300194|КоАП
educational|Hk1100243|Кодекс об образовании
seafaring_trade|HK9900321|Кодекс торгового мореплавания
wood|HK0000420|Лесной кодекс
taxing_common|Hk0200166|Налоговый кодекс (Общая часть)
taxing_special|Hk0900071|Налоговый кодекс (Особенная часть)
admin_proc|Hk0600194|ПИКоАП
job|HK9900296|Трудовой кодекс
criminal|HK9900275|Уголовный кодекс
criminal_exec|HK0000365|Уголовно-исполнительный кодекс
criminal_proc|HK9900295|Уголовно-процессуальный кодекс
property_proc|HK9800219|Хозяйственный процессуальный кодекс"

minimumsize=90000
mkdir -p laws_ashx
mkdir -p laws_xml

for i in $DATA; do 
  actualsize=80000
  NAME=`cut -d"|" -f1 <<< $i`
  ID=`cut -d"|" -f2 <<< $i`
  COMMENT=`cut -d"|" -f3 <<< $i`
  echo $NAME $COMMENT
  

  #Пробуем несколько раз, пока не получим файл, т.к. их API глючит
  while [ $actualsize -le $minimumsize ]; do
    sleep 5
    wget "http://etalonline.by/api/Document.ashx?type=Text&regnum="$ID"&date=none&history=0&queryid=&print=false&RNList=&checked=false&RNPA=&typeload=text" -O /tmp/law_tmp
    #curl 'http://etalonline.by/api/Document.ashx' --data 'type=Text&regnum='$ID'&date=none&history=0&queryid=&print=false&RNList=&checked=false&RNPA=&typeload=text' -o /tmp/law_tmp
    actualsize=$(du -b /tmp/law_tmp | cut  -f1)
    echo $actualsize
  done

  xmllint --xpath "string(//Doc/Text)" <<< cat /tmp/law_tmp > /tmp/law_tmp1
  xmllint -format -recover -encode utf-8 /tmp/law_tmp1 > laws_ashx/${NAME}.xml
  #Чистим от <br/> <sup> </sup> будут мешать XML парсингу
  sed -i -e 's/<br\/>/|/g;s/<sup>/\//g;s/<\/sup>//g; s/<b>//g; s/<\/b>//g; s/<\/A>//g; s/<u>//g; s/<\/u>//g; s/<i>//g; s/<\/i>//g;
            s/<A href=.+>//g; s/<A href\=.*\">//g
            s/<span class\=\"\" style\=\"\">//g

            /<\/span>.*<\/p>/s/<\/span>//g
            s/^\s*<\/span>$//g

            s/<span class\=\"\" style=\".*\">//g
            
            /.*<span class\=\"promulgator\"/s/<\/span>//g; s/<span class\=\"promulgator\" style\=\"\">//g

            /.*<span class\=\"onesymbol\"/s/<\/span>//g; s/<span class\=\"onesymbol\">//g
            /.*<span class\=\"articlec\"/s/<\/span>//g;  s/<span class\=\"articlec\" style\=\"\">//g
            /.*<span class\=\"rednoun\"/s/<\/span>//g;   s/<span class\=\"rednoun\" style\=\"\">//g
            /.*<span class\=\"a30\" style\=\"\">/s/<\/span>//g; s/<span class\=\"a30\" style\=\"\">//g
            /.*<span class\=\"a3\" style\=\"\">/s/<\/span>//g; s/<span class\=\"a3\" style\=\"\">//g
            /.*<span class\=\"fontstyle/s/<\/span>//g;   s/<span class\=\"fontstyle1[45]\" style\=\"\">//g' laws_ashx/${NAME}.xml

  ./parse.py "laws_ashx/${NAME}.xml" "laws_xml/${NAME}.xml"

done

echo "-----------------------------"

git diff --name-only

#./parse.py --make-links

#./test_zlib.py

