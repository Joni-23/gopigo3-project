# -*- coding: utf-8 -*-
import random

tuple1 = ('Joulu on joka vuos, mut juhannus ei ou ku kerran kesässä. -Savonlinna 1936'
          ,'Merry Christmas, eiku hyvvää joulua. Nyt ollaan Suomessa! #suomi100', '#OAMK #internetofthings #python #ohjelmoijat #hyvää #joulua'
          ,'Insinöörit ne vaan on  KOMIAMPIA', 'Mita eroa on kamelilla ja insinöörillä? -Kameli voi olla viikon juomatta'
          ,'#suomi100', 'Olen robotti jonka ovat kehittäneet Tommi Joni ja Juuso','#OAMK'
          )

kummeli = ('Asia kunnossa.','Ei työllä, ei taidolla, ei tuskalla, ei järjellä vaan tuurilla!','Erittäin hyvin sanottu siellä perällä!',
'Haista sinä mursu paska!','Hiljaa!','Hyvä palaveri!','Jumaliste Harri, sä oot hullut mies!','Kanada!','Kohta ei oo enää kellään kivaa',
'Kyllä lähtee!','Normipäivä!','Nyt sattu Juhaa leukaan','Se oli tonnin seteli','Speedy on sairaan nopee!','Tämä mies kuuluu parhaaseen A-ryhmään!',
'Ja vaikka minä homo olisinkin, ei sitä minulle itselleni tarvitse kertoa!','Ei täällä saa ryypätä! -Eikö?!','Kauhee kolari! Ja missä on mun toinen kenkä?',
'Legendaarista!','Antakaa määkin huudan, määkin olen kännissä!','Einari nari pieri ja pani! -Vanha vitsi. -Keksi uus apina','Vyt on Keijolla kova käsi!',
'Mitä? -Mitä mitä? Saatana','Mä otan näitä pölypusseja. -Etkä ota, ne maksaa. Saatana. -Mä otan tän toisenki')



def returnTweet():
    rand_item = random.choice(kummeli)
    return rand_item

