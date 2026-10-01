'''
Strikline Calculator
Maxwell Loughan (6/18/26)

    The program takes a strike point and then
    traces it (upstream) until it strikes 
    the wall again. The total length of the 
    feild line is calculated and then the midpoint 
    determined. Two port coordinates are considered;
    The port closest to the inital strike point, 
    and the halfway point along the strikeline.

        NOTICE: This work was continued (and finished in) 'coord_convert.py'

NOTES: 

It appears that the figures from the paper are actually measured fron the centerline of the plasma
(i.e 2cm from the LCFS is the wall/ and here is the po./tor. srike point in that configuration
 The centerline of the plasma in the equi3D file is NOT structured in this way.
 It is measured by taking the tor/pol angle from the center of HSX (R, theta, phi)

 What we can do is take plot the center-feild line inside the STL of HSX,
 and then us that as a strting point for the strike points. 



'''
whole_thing = True
# Strikeline coordinates from 'HSX as an example of a resilient non-resonant divertor' FIG 13

Inital_strike_line_point = [0.45, 3.5] #  [Tor. Angle (radians), Pol. Angle (radians)]

mgrid = True

if mgrid == True:
    hill_8 = False
else:
    hill_8 = True

MagneticAxis_mgrid = [ #(R, Z, Phi) with R and Z beiong measure from the centroid of HSX
   (1.4453625109087180,        7.6536892932571864E-009,   0.0000000000000000),     
   (1.4446661510652354,        1.3916437410291331E-002,   1.0000000000000000),     
   (1.4425934055391467,        2.7734919991645974E-002,   2.0000000000000000),     
   (1.4391837136616863,        4.1357044785005029E-002,   3.0000000000000000),     
   (1.4344808207194160,        5.4683851416820556E-002,   4.0000000000000000),     
   (1.4285205663015199,        6.7616865874825266E-002,   5.0000000000000000),     
   (1.4213369430297265,        8.0060958090727358E-002,   6.0000000000000000),    
   (1.4129805580566697,        9.1928527277101935E-002,   7.0000000000000000),     
   (1.4035318002457273,       0.10314281117978337,        8.0000000000000000),     
   (1.3930943186993994,       0.11363773937662505,        9.0000000000000000),     
   (1.3817716260265969,       0.12335389609032645,        10.000000000000000),     
   (1.3696461451462678,       0.13223400280217223,        11.000000000000000),     
   (1.3567796476013663,       0.14022308061781258,        12.000000000000000),     
   (1.3432360102109275,       0.14727524403593623,        13.000000000000000),     
   (1.3291082537768555,       0.15336299019766608,        14.000000000000000),     
   (1.3145273659305956,       0.15848100209765661,        15.000000000000000),     
   (1.2996432787085632,       0.16263892177390690,        16.000000000000000),     
   (1.2845905583133794,       0.16584640393296771,        17.000000000000000),     
   (1.2694649464783843,       0.16810198383725272,        18.000000000000000),     
   (1.2543271818602670,       0.16939526324846405,        19.000000000000000),     
   (1.2392275488102371,       0.16972093442230976,        20.000000000000000),     
   (1.2242314716808635,       0.16909453253013904,        21.000000000000000),     
   (1.2094301076919975,       0.16755960265894995,        22.000000000000000),     
   (1.1949317675641897,       0.16518185506019839,        23.000000000000000),     
   (1.1808416647804341,       0.16203389153904116,        24.000000000000000),     
   (1.1672433753005296,       0.15817994530208079,        25.000000000000000),     
   (1.1541921322958550,       0.15366942776858597,        26.000000000000000),     
   (1.1417206624486242,       0.14854124346715375,        27.000000000000000),     
   (1.1298507247299152,       0.14283380102570550,        28.000000000000000),     
   (1.1186026267415679,       0.13659350576086329,        29.000000000000000),     
   (1.1079989016019387,       0.12987710288532603,       30.0000000000000000),     
   (1.0980627524797810,       0.12274747211765606,        31.000000000000000),     
   (1.0888142368113753,       0.11526575872019972,        32.000000000000000),     
   (1.0802671428777582,       0.10748389448004043,        33.000000000000000),     
   (1.0724280649825182,        9.9440650772152264E-002,   34.000000000000000),     
   (1.0652975726002758,        9.1162278900729588E-002,   35.000000000000000),     
   (1.0588724362881166,        8.2666744282354210E-002,   36.000000000000000),     
   (1.0531477738205492,        7.3969419078190282E-002,   37.000000000000000),     
   (1.0481184026244028,        6.5088051074977629E-002,   38.000000000000000),     
   (1.0437792365043190,        5.6045530408838154E-002,   39.000000000000000),     
   (1.0401249982321108,        4.6869948825826908E-002,   40.000000000000000),     
   (1.0371497418582285,        3.7592344604754420E-002,   41.000000000000000),     
   (1.0348466776834730,        2.8243174020319870E-002,   42.000000000000000),     
   (1.0332086002375376,        1.8848861815441487E-002,   43.000000000000000),     
   (1.0322289105525135,        9.4297125109440039E-003,   44.000000000000000),    
   (1.0319029155288753,        2.1121692841989730E-009,   45.000000000000000),     
   (1.0322289106188780,       -9.4297082766645786E-003,   46.000000000000000),     
   (1.0332086003687857,       -1.8848857558180512E-002,   47.000000000000000),     
   (1.0348466778788949,       -2.8243169737069869E-002,   48.000000000000000),     
   (1.0371497421158091,       -3.7592340291629077E-002,   49.000000000000000),     
   (1.0401249985485426,       -4.6869944481963258E-002,   50.000000000000000),     
   (1.0437792368786729,       -5.6045526036185879E-002,   51.000000000000000),     
   (1.0481184030576201,       -6.5088046674549191E-002,   52.000000000000000),     
   (1.0531477743116358,       -7.3969414654635440E-002,   53.000000000000000),     
   (1.0588724368390285,       -8.2666739835241004E-002,   54.000000000000000),     
   (1.0652975732118530,       -9.1162274429979678E-002,   55.000000000000000),     
   (1.0724280656569953,       -9.9440646270098812E-002,   56.000000000000000),     
   (1.0802671436142919,      -0.10748388993362906,        57.000000000000000),     
   (1.0888142376054457,      -0.11526575411057476,        58.000000000000000),     
   (1.0980627533224137,      -0.12274746742638173,        59.000000000000000),     
   (1.1079989024835011,      -0.12987709810097059,        60.000000000000000),     
   (1.1186026276594254,      -0.13659350088503283,        61.000000000000000),     
   (1.1298507256905335,      -0.14283379606904009,        62.000000000000000),     
   (1.1417206634694548,      -0.14854123844492897,        63.000000000000000),     
   (1.1541921333914329,      -0.15366942268681610,        64.000000000000000),     
   (1.1672433764650423,      -0.15817994014459108,        65.000000000000000),     
   (1.1808416659705441,      -0.16203388626144968,        66.000000000000000),     
   (1.1949317687244356,      -0.16518184961977442,        67.000000000000000),     
   (1.2094301087845714,     -0.16755959703716244 ,        68.000000000000000),    
   (1.2242314727201586,      -0.16909452675068293,        69.000000000000000),     
   (1.2392275498407097,      -0.16972092852138010,        70.000000000000000),     
   (1.2543271829267706,      -0.16939525725093788,        71.000000000000000),     
   (1.2694649475994917,      -0.16810197774651561,        72.000000000000000),     
   (1.2845905594428852,      -0.16584639771597043,        73.000000000000000),     
   (1.2996432797204580,      -0.16263891537216918,        74.000000000000000),     
   (1.3145273667197450,      -0.15848099548404085,        75.000000000000000),     
   (1.3291082543584953,      -0.15336298340775853,        76.000000000000000),     
   (1.3432360106785939,      -0.14727523712273644,        77.000000000000000),     
   (1.3567796480101346,      -0.14022307360187555,        78.000000000000000),     
   (1.3696461454903901,      -0.13223399567161265,        79.000000000000000),     
   (1.3817716262242612,      -0.12335388882380066,        80.000000000000000),     
   (1.3930943186301705,      -0.11363773196665292,        81.000000000000000),     
   (1.4035317998732819,      -0.10314280365297689,        82.000000000000000),     
   (1.4129805574261669,       -9.1928519667973871E-002,   83.000000000000000),     
   (1.4213369422072819,       -8.0060950418209043E-002,   84.000000000000000),     
   (1.4285205652951207,       -6.7616858136724106E-002,   85.000000000000000),     
   (1.4344808194728862,       -5.4683843608891114E-002,   86.000000000000000),     
   (1.4391837121054281,       -4.1357036918745552E-002,   87.000000000000000),     
   (1.4425934036468506,       -2.7734912094277326E-002,   88.000000000000000),     
   (1.4446661488719406,       -1.3916429505110678E-002,   89.000000000000000),     

    ]

MagneticAxis_hill_8 = [
    (1.4453625109087180,        7.6536892932571864E-009,   0.0000000000000000),     
    (1.4446661510652354,        1.3916437410291331E-002,   1.0000000000000000 ),    
    (1.4425934055391467,        2.7734919991645974E-002,   2.0000000000000000 ),    
    (1.4391837136616863,        4.1357044785005029E-002,   3.0000000000000000 ),    
    (1.4344808207194160,        5.4683851416820556E-002,   4.0000000000000000 ),    
    (1.4285205663015199,        6.7616865874825266E-002,   5.0000000000000000 ),    
    (1.4213369430297265,        8.0060958090727358E-002,   6.0000000000000000 ),    
    (1.4129805580566697,        9.1928527277101935E-002,   7.0000000000000000 ),    
    (1.4035318002457273,       0.10314281117978337,        8.0000000000000000 ),    
    (1.3930943186993994,       0.11363773937662505,        9.0000000000000000 ),   
    (1.3817716260265969,       0.12335389609032645,        10.000000000000000 ),    
    (1.3696461451462678,       0.13223400280217223,        11.000000000000000 ),    
    (1.3567796476013663,       0.14022308061781258,        12.000000000000000 ),    
    (1.3432360102109275,       0.14727524403593623,        13.000000000000000 ),    
    (1.3291082537768555,       0.15336299019766608,        14.000000000000000 ),    
    (1.3145273659305956,       0.15848100209765661,        15.000000000000000 ),    
    (1.2996432787085632,       0.16263892177390690,        16.000000000000000 ),    
    (1.2845905583133794,       0.16584640393296771,        17.000000000000000 ),    
    (1.2694649464783843,       0.16810198383725272,        18.000000000000000 ),    
    (1.2543271818602670,       0.16939526324846405,        19.000000000000000 ),    
    (1.2392275488102371,       0.16972093442230976,        20.000000000000000 ),    
    (1.2242314716808635,       0.16909453253013904,        21.000000000000000 ),   
    (1.2094301076919975,      0.16755960265894995 ,       22.000000000000000  ),   
    (1.1949317675641897,      0.16518185506019839 ,       23.000000000000000  ),   
    (1.1808416647804341,      0.16203389153904116 ,       24.000000000000000  ),   
    (1.1672433753005296,       0.15817994530208079,        25.000000000000000 ),    
    (1.1541921322958550,       0.15366942776858597,        26.000000000000000 ),   
    (1.1417206624486242,       0.14854124346715375,        27.000000000000000 ),    
    (1.1298507247299152,       0.14283380102570550,        28.000000000000000 ),    
    (1.1186026267415679,       0.13659350576086329,        29.000000000000000 ),    
    (1.1079989016019387,       0.12987710288532603,        30.000000000000000 ),    
    (1.0980627524797810,       0.12274747211765606,        31.000000000000000 ),    
    (1.0888142368113753,       0.11526575872019972,        32.000000000000000 ),    
    (1.0802671428777582,       0.10748389448004043,        33.000000000000000 ),    
    (1.0724280649825182,        9.9440650772152264E-002,   34.000000000000000 ),    
    (1.0652975726002758,        9.1162278900729588E-002,   35.000000000000000 ),    
    (1.0588724362881166,        8.2666744282354210E-002,   36.000000000000000 ),    
    (1.0531477738205492,        7.3969419078190282E-002,   37.000000000000000 ),    
    (1.0481184026244028,        6.5088051074977629E-002,   38.000000000000000 ),    
    (1.0437792365043190,        5.6045530408838154E-002,   39.000000000000000 ),    
    (1.0401249982321108,        4.6869948825826908E-002,   40.000000000000000 ),    
    (1.0371497418582285,        3.7592344604754420E-002,   41.000000000000000 ),    
    (1.0348466776834730,        2.8243174020319870E-002,   42.000000000000000 ),    
    (1.0332086002375376,        1.8848861815441487E-002 ,  43.000000000000000 ),    
    (1.0322289105525135,        9.4297125109440039E-003,   44.000000000000000 ),    
    (1.0319029155288753,        2.1121692841989730E-009,   45.000000000000000 ),    
    (1.0322289106188780,       -9.4297082766645786E-003,   46.000000000000000 ),    
    (1.0332086003687857,       -1.8848857558180512E-002,   47.000000000000000 ),    
    (1.0348466778788949,       -2.8243169737069869E-002,   48.000000000000000 ),    
    (1.0371497421158091,       -3.7592340291629077E-002,   49.000000000000000 ),    
    (1.0401249985485426,       -4.6869944481963258E-002,   50.000000000000000 ),    
    (1.0437792368786729,       -5.6045526036185879E-002,   51.000000000000000 ),    
    (1.0481184030576201,       -6.5088046674549191E-002,   52.000000000000000 ),    
    (1.0531477743116358,       -7.3969414654635440E-002,   53.000000000000000 ),    
    (1.0588724368390285,       -8.2666739835241004E-002,   54.000000000000000 ),    
    (1.0652975732118530,       -9.1162274429979678E-002,   55.000000000000000 ),    
    (1.0724280656569953,       -9.9440646270098812E-002,   56.000000000000000 ),    
    (1.0802671436142919,      -0.10748388993362906,        57.000000000000000 ),    
    (1.0888142376054457,      -0.11526575411057476,        58.000000000000000 ),    
    (1.0980627533224137,      -0.12274746742638173,        59.000000000000000 ),    
    (1.1079989024835011,      -0.12987709810097059,        60.000000000000000 ),    
    (1.1186026276594254,      -0.13659350088503283,        61.000000000000000 ),    
    (1.1298507256905335,      -0.14283379606904009,        62.000000000000000 ),    
    (1.1417206634694548,      -0.14854123844492897,        63.000000000000000 ),    
    (1.1541921333914329,      -0.15366942268681610,        64.000000000000000 ),    
    (1.1672433764650423,      -0.15817994014459108,        65.000000000000000 ),    
    (1.1808416659705441,      -0.16203388626144968,        66.000000000000000 ),   
    (1.1949317687244356,      -0.16518184961977442,        67.000000000000000 ),    
    (1.2094301087845714,      -0.16755959703716244,        68.000000000000000 ),    
    (1.2242314727201586,      -0.16909452675068293,        69.000000000000000 ),    
    (1.2392275498407097,      -0.16972092852138010,        70.000000000000000 ),    
    (1.2543271829267706,      -0.16939525725093788,        71.000000000000000 ),    
    (1.2694649475994917,      -0.16810197774651561,        72.000000000000000 ),    
    (1.2845905594428852,      -0.16584639771597043,        73.000000000000000 ),    
    (1.2996432797204580,      -0.16263891537216918,        74.000000000000000 ),    
    (1.3145273667197450,      -0.15848099548404085,        75.000000000000000 ),    
    (1.3291082543584953,      -0.15336298340775853,        76.000000000000000 ),    
    (1.3432360106785939,      -0.14727523712273644,        77.000000000000000 ),    
    (1.3567796480101346,      -0.14022307360187555,        78.000000000000000 ),    
    (1.3696461454903901,      -0.13223399567161265,        79.000000000000000 ),    
    (1.3817716262242612,      -0.12335388882380066,        80.000000000000000 ),    
    (1.3930943186301705,      -0.11363773196665292,        81.000000000000000 ),    
    (1.4035317998732819,      -0.10314280365297689,        82.000000000000000 ),    
    (1.4129805574261669,       -9.1928519667973871E-002,   83.000000000000000 ),    
    (1.4213369422072819,       -8.0060950418209043E-002,   84.000000000000000 ),    
    (1.4285205652951207,       -6.7616858136724106E-002,   85.000000000000000 ),    
    (1.4344808194728862,       -5.4683843608891114E-002,   86.000000000000000 ),    
    (1.4391837121054281,       -4.1357036918745552E-002,   87.000000000000000 ),    
    (1.4425934036468506,      -2.7734912094277326E-002 ,  88.000000000000000  ),   
    (1.4446661488719406,       -1.3916429505110678E-002,   89.000000000000000) ,    

]
Magnetic_axis_mgrid_RAW = [ #raw data from the equi3d file (mgrid)

 (  1.4453625166835500   ,    4.4976450298311779E-009   , 0.0000000000000000),     
 (  1.4446661502251585   ,     1.3916416302555738E-002  , 1.0000000000000000),     
(   1.4425934054957694   ,     2.7734898924631681E-002  , 2.0000000000000000),     
(   1.4391837143982114   ,     4.1357023791459044E-002  , 3.0000000000000000),     
(   1.4344808222200487   ,     5.4683830529822494E-002  , 4.0000000000000000),     
(   1.4285205685544513   ,     6.7616845129243972E-002  , 5.0000000000000000),     
(   1.4213369460236898   ,     8.0060937523931411E-002  , 6.0000000000000000),     
(   1.4129805617741547   ,     9.1928506927889439E-002  , 7.0000000000000000),     
(   1.4035318046592515   ,    0.10314279108607137       , 8.0000000000000000),     
(   1.3930943237749827   ,    0.11363771957374935       , 9.0000000000000000),     
(   1.3817716317320943   ,    0.12335387661138361       , 10.000000000000000),     
(   1.3696461514571552   ,    0.13223398367976844       , 11.000000000000000),     
(   1.3567796544982129   ,    0.14022306188489089       , 12.000000000000000),     
(   1.3432360176696367   ,    0.14727522572392865       , 13.000000000000000),     
(   1.3291082617587329   ,    0.15336297233265600       , 14.000000000000000),     
(   1.3145273743801660   ,    0.15848098469755389       , 15.000000000000000),     
(   1.2996432875620747   ,    0.16263890484953061       , 16.000000000000000),     
(   1.2845905675125664   ,    0.16584638749266978       , 17.000000000000000),     
(   1.2694649559795395   ,    0.16810196789113929       , 18.000000000000000),     
(   1.2543271916330914   ,    0.16939524780847579       , 19.000000000000000),     
(   1.2392275588292792   ,    0.16972091949799104       , 20.000000000000000),     
(   1.2242314819164029   ,    0.16909451812308751       , 21.000000000000000),     
(   1.2094301181057456   ,    0.16755958875967952       , 22.000000000000000),     
(   1.1949317781113713   ,    0.16518184164965857       , 23.000000000000000),     
(   1.1808416754160651   ,    0.16203387859407858       , 24.000000000000000),     
(   1.1672433859857487   ,    0.15817993280149539       , 25.000000000000000),     
(   1.1541921430010877   ,    0.15366941569627918       , 26.000000000000000),     
(   1.1417206731530494   ,    0.14854123181133311       , 27.000000000000000),     
(   1.1298507354188139   ,    0.14283378977562441       , 28.000000000000000),     
(   1.1186026374034173   ,    0.13659349490345937       , 29.000000000000000),     
(   1.1079989122262510   ,    0.12987709240343978       , 30.000000000000000),     
(   1.0980627630559490   ,    0.12274746199035046       , 31.000000000000000),     
(   1.0888142473284215   ,    0.11526574892471500       , 32.000000000000000),     
(   1.0802671533246802   ,    0.10748388499441903       , 33.000000000000000),     
(   1.0724280753490392   ,     9.9440641577535266E-002  , 34.000000000000000),     
(   1.0652975828776301   ,     9.1162269982675237E-002  , 35.000000000000000),     
(   1.0588724464696768   ,     8.2666735630979427E-002  , 36.000000000000000),     
(   1.0531477839021344   ,     7.3969410687356130E-002  , 37.000000000000000),     
(   1.0481184126041772   ,     6.5088042940917634E-002  , 38.000000000000000),     
(   1.0437792463823721   ,     5.6045522528648375E-002  , 39.000000000000000),     
(   1.0401250080097573   ,     4.6869941196101862E-002  , 40.000000000000000),     
(   1.0371497515372514   ,     3.7592337220541193E-002  , 41.000000000000000),     
(   1.0348466872654902   ,     2.8243166874486688E-002  , 42.000000000000000),     
(   1.0332086097236182   ,     1.8848854898550385E-002  , 43.000000000000000),     
(   1.0322289199431327   ,     9.4297058116814131E-003  , 44.000000000000000),     
(   1.0319029248241482   ,    -4.3817051966153336E-009  , 45.000000000000000),     
(   1.0322289198189352   ,    -9.4297145770262589E-003  , 46.000000000000000),     
(   1.0332086094741626   ,    -1.8848863675234442E-002  , 47.000000000000000),     
(   1.0348466868907669   ,    -2.8243175678395453E-002  , 48.000000000000000),     
(   1.0371497510359793   ,    -3.7592346061840809E-002  , 49.000000000000000),     
(   1.0401250073792312   ,    -4.6869950083070856E-002  , 50.000000000000000),     
(   1.0437792456221209   ,    -5.6045531468517727E-002  , 51.000000000000000),     
(   1.0481184117156259   ,    -6.5088051937961369E-002  , 52.000000000000000),     
(   1.0531477828851052   ,    -7.3969419749685697E-002  , 53.000000000000000),     
(   1.0588724453276319   ,    -8.2666744764050573E-002  , 54.000000000000000),     
(   1.0652975816138714   ,    -9.1162279196579543E-002  , 55.000000000000000),     
(   1.0724280739693333   ,    -9.9440650880153220E-002  , 56.000000000000000),     
(   1.0802671518326601   ,   -0.10748389439356024       , 57.000000000000000),     
(   1.0888142457245762   ,   -0.11526575842631433       , 58.000000000000000),     
(   1.0980627613362286   ,   -0.12274747160216712       , 59.000000000000000),     
(   1.1079989103852259   ,   -0.12987710213871925       , 60.000000000000000),     
(   1.1186026354418055   ,   -0.13659350478474416       , 61.000000000000000),     
(   1.1298507333463521   ,   -0.14283379983034256       , 62.000000000000000),     
(   1.1417206709924512   ,   -0.14854124206937028       , 63.000000000000000),     
(   1.1541921407772378   ,   -0.15366942617994214       , 64.000000000000000),     
(   1.1672433837114418   ,   -0.15817994351662498       , 65.000000000000000),     
(   1.1808416730764069   ,   -0.16203388952586997       , 66.000000000000000),     
(   1.1949317756875024   ,   -0.16518185279025613       , 67.000000000000000),     
(   1.2094301155994001   ,   -0.16755960012458673       , 68.000000000000000),     
(   1.2242314793780904   ,   -0.16909452976214817       , 69.000000000000000),     
(   1.2392275563326902   ,   -0.16972093146202130       , 70.000000000000000),     
(   1.2543271892482133   ,   -0.16939526012752826       , 71.000000000000000),     
(   1.2694649537546576   ,   -0.16810198057057832       , 72.000000000000000),     
(   1.2845905654458540   ,   -0.16584640050426858       , 73.000000000000000),     
(   1.2996432855912263   ,   -0.16263891814390347       , 74.000000000000000),     
(   1.3145273724771296   ,   -0.15848099825628312       , 75.000000000000000),     
(   1.3291082600145454   ,   -0.15336298619211125       , 76.000000000000000),     
(   1.3432360162388699   ,   -0.14727523992532268       , 77.000000000000000),     
(   1.3567796534796535   ,   -0.14022307642603560       , 78.000000000000000),     
(   1.3696461508806852   ,   -0.13223399852077161       , 79.000000000000000),     
(   1.3817716315561166   ,   -0.12335389170243813       , 80.000000000000000),     
(   1.3930943239299769   ,   -0.11363773487917266       , 81.000000000000000),     
(   1.4035318051656767   ,   -0.10314280660186576       , 82.000000000000000),     
(   1.4129805627285634   ,    -9.1928522652924047E-002  , 83.000000000000000),     
(   1.4213369475303874   ,    -8.0060953436787277E-002  , 84.000000000000000),     
(   1.4285205706485962   ,    -6.7616861185814767E-002  , 85.000000000000000),     
(   1.4344808248711980   ,    -5.4683846685673450E-002  , 86.000000000000000),     
(   1.4391837175690836   ,    -4.1357040020649181E-002  , 87.000000000000000),     
(   1.4425934091982562   ,    -2.7734915218326418E-002  , 88.000000000000000),     
(   1.4446661545293829   ,    -1.3916432647458734E-002  , 89.000000000000000),     

]
def Coord_convert(Toroidal_angle, Poloidal_angle):
    '''
THIS function will calculate the wall coords from the magnetic axis
    '''

import numpy as np
import math
import pyvista as pv
def spherical_to_cartesian(r, theta, phi, Deg=True):
    """
    Converts spherical coordinates to Cartesian coordinates (Scalar version).
    Angles (theta, phi) must be in radians.
    if Deg=True, then system is in degreees
    """
    if Deg == True: 
        
        # theta_deg = np.degrees(theta)
        # phi_deg = np.degrees(phi)
        # # phi_deg = phi
        # r_deg =  r

        # x_deg = r_deg * math.sin(theta) * math.cos(phi)
        # y_deg = r_deg * math.sin(theta) * math.sin(phi)
        # z_deg = r_deg * math.cos(theta)
        
        theta_rad = np.radians(theta)
        phi_rad = np.radians(phi)

        [x_deg, y_deg, z_deg] = pv.spherical_to_cartesian(r, phi_rad, theta_rad)

        return [x_deg, y_deg, z_deg]
    else:
        x = r * math.sin(theta) * math.cos(phi)
        y = r * math.sin(theta) * math.sin(phi)
        z = r * math.cos(theta)
        
        return [x, y, z]

def cylindrical_to_cartesian(r, phi, z, Deg=True):
    """
    Converts cylindrical coordinates (R, Phi, Z) to Cartesian coordinates (X, Y, Z).
    Assumes phi is provided in radians.
    """
    if Deg == True: 
        #convert from degrees to rads for np
        phi_rad = np.radians(phi)
        x_rad = r * math.cos(phi_rad)
        y_rad = r * math.sin(phi_rad)
        return [x_rad, y_rad, z ]
    else:
        x = r * math.cos(phi)
        y = r * math.sin(phi)
        return [x, y, z]


def cartesian_to_cylindrical(x, y, z, Deg=True):
    """
    Converts Cartesian coordinates (x, y, z) to Cylindrical coordinates (r, z, phi).
    That is the format used by the Fieldlines.trace(..) module

    Phi is returned in radians.
    switch to degrees to do degrees, which is what HSX works with
    """
    r = math.sqrt(x**2 + y**2)
    if Deg == True: 
        phi = math.degrees(math.atan2(y, x))
    else:
        phi = math.atan2(y, x)
    
    return r, z, phi
###################################################

Cart_Coords_Magnetic_axis = []
if mgrid == True:
    # for coord in MagneticAxis_mgrid:
    for coord in Magnetic_axis_mgrid_RAW:
        r_cyl = coord[0]
        z_cyl = coord[1]
        phi_cyl = coord[2]
        [x_cart, y_cart, z_cart] = cylindrical_to_cartesian(r_cyl, phi_cyl, z_cyl)
        array = np.array([float(x_cart), float(y_cart), float(z_cart)])
        Cart_Coords_Magnetic_axis.append(array)  # Use .tolist() to add as a list of arrays
        # print(f'Did {coord}')
else: 
    for coord in MagneticAxis_hill_8:
        r_cyl = coord[0]
        z_cyl = coord[1]
        phi_cyl = coord[2]
        [x_cart, y_cart, z_cart] = cylindrical_to_cartesian(r_cyl, phi_cyl, z_cyl)
        array = np.array([float(x_cart), float(y_cart), float(z_cart)])
        Cart_Coords_Magnetic_axis.append(array)  # Use .tolist() to add as a list of arrays
        # print(f'Did {coord}')
    
print("here is the list")
print(Cart_Coords_Magnetic_axis[0])

def StrikeLine_Line_Vector(Toroidal_angle, Poloidal_angle) : # both in radians

        # Convert radians to degrees 
        Tor_in_Deg = round(np.degrees(Toroidal_angle))
        print(f'toroidal angle is {Tor_in_Deg}')
        if Tor_in_Deg > 90 :
            print('SORRY that number is bigger than 90, readjust to fit into quadrant')
        # find coordinates for the toroidal angle
        coordinate_of_magnetic_line_intersection = Cart_Coords_Magnetic_axis[(Tor_in_Deg)]
##############
        start_point = np.array(coordinate_of_magnetic_line_intersection)
        
        theta = Toroidal_angle  
        phi = Poloidal_angle   
        length = 0.2           
        print(f'poloidal angle is {np.degrees(Poloidal_angle)}')
        direction = np.array([
            np.sin(phi) * np.cos(theta),
            np.sin(phi) * np.sin(theta),
            np.cos(phi)
        ])
        endpoint = start_point + (direction * length)

        return coordinate_of_magnetic_line_intersection, endpoint



if whole_thing == True: 
    import pyvista as pv
    import numpy as np
    from moose import geometry
    from flare import model
    from flare.analysis import bfield
    # probe_length = 0.05
    # Activate verbose mode
    verbose = True
    InteractiveMode = True # interactive STL selection tool mode
    PrintZeros = False #print b field values that are [0,0,0]
    # ModelChoice = 'placeholder'
    if mgrid == True:
        ModelChoice = 'mgrid'
    if hill_8 == True:
        ModelChoice = 'hill_8'
    # ModelComparison = True # make comparisons between models (model 1 and 2)

    # Set up a list to temp. catch the point selections
    # Click history centroids
    ClickedCentroids = []
    pv.set_jupyter_backend('trame') # attempt to get this to run with GPU -- ignore
   
    def main():
        ########### LIST of PORTS ################
        port_dict = {}
        ####################################################

        # HSX Mesh STL
        stl_mesh = pv.read("HSX_ASSEMBLY_RECONSTRUCTED.STL")
        # /home/madmax/Projects/HSX_wisp_gauges/HSX_ASSEMBLY_RECONSTRUCTED.STL
        # Wall surface from moose geometry 
        wall_grids = geometry.Torosurf.loadtxt("./wall_3cm_from_plasma_full.txt").grid.vtk()
        
        # Convert the first structured grid to a surface PolyData geometry
        wall_pv = pv.wrap(wall_grids[0])
        wall_surface = wall_pv.extract_surface()

        # Interactive plotting environment
        plotter = pv.Plotter()
        plotter.background_color = "black"
        
        plotter.add_mesh( #Mesh for HSX
            stl_mesh,
            # style="wireframe",
            color="spring_green",
            label="HSX Assembly",
            opacity=0.3
        )
        
        plotter.add_mesh( #Mesh for wall surface (assuming that this is the plasma edge)
            wall_surface,
            color="purple",
            label="Wall Surface",
            opacity=0.5
        )

        points = Cart_Coords_Magnetic_axis
        
        # points = MagneticAxis_mgrid
        line_mesh = pv.lines_from_points(points)

        plotter.add_mesh( #Mesh for Magnetic center line
            line_mesh,
            color="blue",
            label="Mag. Center",
            line_width=10
        )

        centerline_coord, strike_vector = StrikeLine_Line_Vector(0.45, 3.5)
        HSX_center = np.array([0.0, 0.0, 0.0])
        line_point = np.array(centerline_coord)

        Center_to_magnetic_line = pv.Line(pointa=HSX_center, pointb=line_point)

        plotter.add_mesh( #Mesh for centroid to Magnetic center line
            Center_to_magnetic_line,
            color="red",
            label="Center to Magnetic Center",
            line_width=2
        )

        Strikeline_vector = pv.Line(pointa=centerline_coord, pointb=strike_vector, resolution=19)
        vector_points_list = Strikeline_vector.points.tolist() # making a list of points along the line to start a B-field trace

        if verbose == True: print(f"Total poloidal points: {len(vector_points_list)}")
        if verbose == True: print("First point (magnetic axis):", vector_points_list[0])
        if verbose == True: print("Last point (just outside the vessel):", vector_points_list[-1])
        print(vector_points_list)

        plotter.add_mesh( #Mesh for strikline vector
            Strikeline_vector,
            color="green",
            label="strikline vector",
            line_width=2
        )
        vector_points_list_array = np.array(vector_points_list)
        plotter.add_points( #Mesh for strike vector points
            vector_points_list_array,
            color='pink', 
            point_size=5, 
            # render_points_as_spheres=True
        )
        #Attained strike coords: [1.0014998  0.48863193 0.04729004] and [0.9992501  0.4875452  0.04062013]
        strike_coords = np.array([[1.0014998,  0.48863193, 0.04729004]])

        plotter.add_points( #Mesh for strike point
            strike_coords,
            color='yellow', 
            point_size=25, 
            # render_points_as_spheres=True
        )
        # points, face_ids = stl_mesh.ray_trace(centerline_coord, strike_vector, plot=True)
        
        print(f"Hit detected at coordinates: {points[0]}")
        ###
        # points = np.array(Cart_Coords_Magnetic_axis)
        # points = Cart_Coords_Magnetic_axis

        # line_mesh = pv.lines_from_points(points)
        # line_mesh.plot(color='blue', line_width=10)
        ###

        
        # Initialize external field configurations
        # Here we should be able to put in a model to work with 
            # Note: Location of file on Max's Windows laptop running WSL in VScode
            # \\wsl.localhost\Ubuntu\home\madmax\DATABASE\flare\HSX\
            # drop files in here with the configurations, and everything should work!
            
       
        if ModelChoice == 'mgrid':
            model.load("HSX/mgrid") # model 1
        if ModelChoice == 'hill_8':
            model.load("HSX/hill_8_config") #model 2

        # Find cell normals to capture true flat face orientations
        mesh = stl_mesh.compute_normals(cell_normals=True, point_normals=False, inplace=False)

        # Container list for the normal (probe) arrow
        current_arrow = [None]
        # Container list for flat surface visuals  
        active_actors = []

        def my_callback(point):

            #Centroid of Port Determination
            
            # Clear previous highlights from the screen
            for actor in active_actors:
                plotter.remove_actor(actor)
            active_actors.clear()

            # id a seed cell to use nearest to the clicked point
            seed_cell_id = mesh.find_closest_cell(point)
            if seed_cell_id == -1:
                return
            seed_normal = mesh.cell_normals[seed_cell_id]

            # Using a flood-fill method, identifiy a flat area to find the centroid
            # We are going to set the angle tolerance between cells to 5 deg 
            angle_tolerance_deg = 5.0  
            cos_tolerance = np.cos(np.radians(angle_tolerance_deg))

            # By finding cells next to the slected cell, we can deterimine
            # the number of flat cells, and add them to a list

            visited = set() # create an empty set to append to later for neighbors
            queue = [seed_cell_id] # queue list 
            visited.add(seed_cell_id) # visitied cells
        
            flat_cell_ids = [] # list for the flat surface catalog

            # Flood-fill surface determination
            # We make a loop that checks neighboring cells for angular similarity 
            while queue:
                current_cell = queue.pop(0) # remove and return the first element (queue)
                flat_cell_ids.append(current_cell)
                
                # Neighbors are cells that share an edge in the mesh
                neighbors = mesh.cell_neighbors(current_cell, connections="edges")
                
                for neighbor in neighbors:
                    if neighbor not in visited:

                        neighbor_normal = mesh.cell_normals[neighbor]
                        # Use dot product to check if the neighbor normal points the same direction
                        dot_product = np.dot(seed_normal, neighbor_normal)

                        if dot_product >= cos_tolerance:
                            visited.add(neighbor)
                            queue.append(neighbor)
            
            # Now we can compute the centroid of the flat reigion 
            # Extract the flat reigion
            flat_region_mesh = mesh.extract_cells(flat_cell_ids)

            # Compute the ave. positions of the cell centers 
            cell_centers = flat_region_mesh.cell_centers().points
            region_centroid = np.mean(cell_centers, axis=0) # This is ideally the WISP probe position

            # Highlight the flat area
            region_actor = plotter.add_mesh(
                flat_region_mesh, 
                color="light blue", 
                show_edges=True, 
                line_width=1, 
                name="highlighted_flat_region"
            )
            # Store actor(s) to handle removal on next click
            active_actors.extend([region_actor])

            # B-feild Evaluation at Centroid and Data Display
            bfield_eval = bfield.eval(region_centroid[0], region_centroid[1], region_centroid[2])
            print(f"\n--- Selection Registered ---")
            if verbose == True: print(f"Clicked coordinate: [{point[0]:.4f}, {point[1]:.4f}, {point[2]:.4f}]")
            if verbose == True:print(f"Flat region includes {len(flat_cell_ids)} cells.")
            if verbose == True:print(f"Port centroid coordinates: {region_centroid}")
            if verbose == True:print(f"B-field at centroid of port opening (flat face): {bfield_eval}")
            
            # this is a temp. way to append the clicked centoids to the list to get port IDs
            ClickedCentroids.extend([region_centroid])

            # Index of the specific triangular centroid
            cell_index = mesh.find_closest_cell(region_centroid)
            
            # Normal vector array to the cell centroid
            raw_normal = mesh['Normals'][cell_index]
            
            # Invert the vector direction to point inward toward the internal volume
            inward_normal = raw_normal * -1
            if verbose == True: print(f"Inward Face Normal (vector of WISP Gauge extension): [{inward_normal[0]:.4f}, {inward_normal[1]:.4f}, {inward_normal[2]:.4f}]")
            
            # Erase the previous arrow actor
            if current_arrow[0] is not None:
                plotter.remove_actor(current_arrow[0])
                
            # Position the vector arrow on the centroid
            # Scale to 0.05 assuming mesh is in meters (5 cm probe length)
            probe_length = 0.05 ###################### PLEASE VERIFY ###########################
            # while True:
            #     try: 
            #         probe_length = float(input("What probe length (0.05 m default)? : "))
            #         break
            #     except ValueError:
            #         print('Input an integer or decimal')

            arrow_mesh = pv.Arrow(start=region_centroid, direction=inward_normal, scale= probe_length) 
            
            # Evaluate the magnetic feild at the probe tip 
            # -> Add the normal vector to the centroid point to make new point at tip of vector
            #   -> Evaluate B-feild at point that is at tip of vector
            ProbeTip_coordinate_raw = ((region_centroid[0] + (probe_length * inward_normal[0])), (region_centroid[1] + (probe_length * inward_normal[1])), (region_centroid[2] + (probe_length * inward_normal[2])))
            ProbeTip_coordinate = [float(x) for x in ProbeTip_coordinate_raw]
            if verbose == True: print(f"coordinate of probe tip: {ProbeTip_coordinate}")
            ProbeTip_B = bfield.eval((region_centroid[0] + (probe_length * inward_normal[0])), (region_centroid[1] + (probe_length * inward_normal[1])), (region_centroid[2] + (probe_length * inward_normal[2])))
            
            # if ProbeTip_B == '[0. 0. 0.]':
            #     if PrintZeros == True:
            #         print(f"B-feild at WISP Gauge tip: {ProbeTip_B}")
            #     else:
            #         pass
            # else:
            #     print(f"B-feild at WISP Gauge tip: {ProbeTip_B}")
            print(f"B-feild at WISP Gauge tip: {ProbeTip_B}")

            # Add arrow to plotter and track via container list index
            current_arrow[0] = plotter.add_mesh(arrow_mesh, color='red', label="Inward Normal Vector")

        # We will separate things out into quadrants to make selection easy
        # starting from the loaded front facing quandrant and moving CW

    

        ##### GUI window and selector ##### 
        if InteractiveMode == True:     
            # points, face_ids = stl_mesh.ray_trace(centerline_coord, strike_vector, plot=True)

            print(f'Point of strike ; {points}')
            print('')
            plotter.enable_surface_point_picking(callback=my_callback, show_point=True)
            plotter.add_legend()
            plotter.show_axes()
            plotter.show()
            if verbose == True: print('')
            if verbose == True: print('The centroids of each port is: ')
            if verbose == True: print('')
            if verbose == True: print(ClickedCentroids)
        else:
            pass
        


            print('============== Program Ended ==============')
        ###########################################

    if __name__ == "__main__":
        main()
