#include "./calc.h"

int main() {
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
  setvbuf(stdin, NULL, _IONBF, 0);
  // Replace here with Python generated output
  operation_t operations[] = {
    { .oper = '%', .operandA = 314.23572239497753, .operandB = -343.80018153073945 },
    { .oper = '-', .operandA = 440.23960117225056, .operandB = 97.06735072845765 },
    { .oper = '%', .operandA = -101.85126480640992, .operandB = 430.61512281284047 },
    { .oper = '/', .operandA = 26.566683118055153, .operandB = -179.0810006863229 },
    { .oper = '%', .operandA = -70.14572896052726, .operandB = -320.1140167220988 },
    { .oper = '/', .operandA = 466.1142124377461, .operandB = -173.60461194722888 },
    { .oper = '%', .operandA = -2.338062192709174, .operandB = -435.2257228345381 },
    { .oper = '-', .operandA = -214.53669190732774, .operandB = -300.7554748526087 },
    { .oper = '^', .operandA = -98.75553114434364, .operandB = 87.0 },
    { .oper = '*', .operandA = -181.26930852013754, .operandB = -254.2891753858638 },
    { .oper = '+', .operandA = 98.69859205620185, .operandB = -165.9282391293022 },
    { .oper = '+', .operandA = 116.02748073934754, .operandB = 321.984734802748 },
    { .oper = '-', .operandA = 327.17503396056986, .operandB = 389.39911291964813 },
    { .oper = '/', .operandA = 275.89275771392215, .operandB = 485.1321681765701 },
    { .oper = '+', .operandA = 256.6457520589561, .operandB = -267.88161010532775 },
    { .oper = '%', .operandA = 93.16171654064658, .operandB = -47.42472178263847 },
    { .oper = '%', .operandA = -188.83537810065855, .operandB = -42.50856926897927 },
    { .oper = '+', .operandA = 297.4652425999785, .operandB = 114.38208161179807 },
    { .oper = '%', .operandA = 45.272562437363035, .operandB = 126.45364070022879 },
    { .oper = '/', .operandA = 76.3872255137918, .operandB = -202.63547621989466 },
    { .oper = '-', .operandA = -107.4658375019244, .operandB = -195.93756762939284 },
    { .oper = '-', .operandA = -318.00727631418033, .operandB = -202.1613442255964 },
    { .oper = '^', .operandA = 15.237325371187147, .operandB = 69.04397838106345 },
    { .oper = '/', .operandA = 134.78167543723225, .operandB = 246.70382391299904 },
    { .oper = '%', .operandA = 365.5900085787963, .operandB = -458.21015483029527 },
    { .oper = '^', .operandA = -7.455587224905514, .operandB = 15.0 },
    { .oper = '-', .operandA = -448.3995644416161, .operandB = 451.6401344241308 },
    { .oper = '+', .operandA = 195.1954528459836, .operandB = -3.159313392519607 },
    { .oper = '*', .operandA = -242.35096607679327, .operandB = -94.05742243049707 },
    { .oper = '^', .operandA = 61.2322120565459, .operandB = 57.49752960201301 },
    { .oper = '%', .operandA = -48.90609517858468, .operandB = 4.56423488614746 },
    { .oper = '%', .operandA = 377.0848901179586, .operandB = -218.0176934131053 },
    { .oper = '-', .operandA = 436.4717594933577, .operandB = 406.46065665769936 },
    { .oper = '/', .operandA = 152.3297431295647, .operandB = -196.04252329327966 },
    { .oper = '/', .operandA = -244.22569602359835, .operandB = 164.83379467128327 },
    { .oper = '^', .operandA = -32.49558678970489, .operandB = 45.0 },
    { .oper = '+', .operandA = 329.79729366711, .operandB = -200.38340058884228 },
    { .oper = '%', .operandA = -104.65344600547064, .operandB = -197.87130504352746 },
    { .oper = '%', .operandA = 257.8983468906606, .operandB = -316.1366955271675 },
    { .oper = '+', .operandA = 257.91142723632504, .operandB = 319.02451910597506 },
    { .oper = '/', .operandA = -200.2108948167093, .operandB = 424.40589241297664 },
    { .oper = '/', .operandA = 12.634808083532903, .operandB = -3.0147805712556988 },
    { .oper = '/', .operandA = 109.64309992879964, .operandB = 470.4859112961402 },
    { .oper = '%', .operandA = -303.6130095467497, .operandB = -218.82034875074498 },
    { .oper = '*', .operandA = 228.34731272089982, .operandB = -308.0440675454499 },
    { .oper = '^', .operandA = -56.83925458036938, .operandB = 37.0 },
    { .oper = '%', .operandA = -112.71915174806799, .operandB = -369.8345426832743 },
    { .oper = '/', .operandA = -309.5081470478035, .operandB = 399.35840202008114 },
    { .oper = '/', .operandA = -319.825976302458, .operandB = 402.41138054996475 },
    { .oper = '%', .operandA = 138.55118925698957, .operandB = 233.5304639154714 },
    { .oper = '*', .operandA = 252.85094275577183, .operandB = 248.63327757297907 },
    { .oper = '^', .operandA = -87.21972599004201, .operandB = 93.0 },
    { .oper = '^', .operandA = 60.51396748080337, .operandB = 84.93280493871936 },
    { .oper = '/', .operandA = 367.2521504592072, .operandB = -173.27391374434285 },
    { .oper = '+', .operandA = 448.07560706423726, .operandB = 378.0243773867894 },
    { .oper = '+', .operandA = -164.09878927617893, .operandB = -196.68253220137456 },
    { .oper = '/', .operandA = 187.79216150279444, .operandB = 252.15661282803262 },
    { .oper = '%', .operandA = -451.2210317711145, .operandB = 107.42367214064984 },
    { .oper = '^', .operandA = -462.4113231059457, .operandB = 0.45391883469417005 },
    { .oper = '%', .operandA = -218.05685194649337, .operandB = 218.05685194649337 },
    { .oper = '^', .operandA = -2.9335991136411055, .operandB = 0.9880039025773557 },
    { .oper = '+', .operandA = -412.9196101924579, .operandB = 386.8483404652185 },
    { .oper = '%', .operandA = -129.62213340446021, .operandB = 129.62213340446021 },
    { .oper = '^', .operandA = 85.4727225760916, .operandB = 60.60280707580021 },
    { .oper = '%', .operandA = -195.86680296791417, .operandB = 322.7340791332307 },
    { .oper = '^', .operandA = -454.23459218870016, .operandB = 0.5986235243509275 },
    { .oper = '*', .operandA = -150.2774441921585, .operandB = -339.46899096845874 },
    { .oper = '%', .operandA = -298.6111931473824, .operandB = 298.6111931473824 },
    { .oper = '%', .operandA = -348.3287378284605, .operandB = -348.3287378284605 },
    { .oper = '%', .operandA = -191.18370800215104, .operandB = 175.61372397526645 },
    { .oper = '-', .operandA = 277.26225539281256, .operandB = 332.01731164313105 },
    { .oper = '*', .operandA = -123.67882547416389, .operandB = -114.81653092406208 },
    { .oper = '+', .operandA = 351.5064618655932, .operandB = -132.9687035867513 },
    { .oper = '^', .operandA = 28.459710154140247, .operandB = 78.31670312375007 },
    { .oper = '*', .operandA = 429.42502646561604, .operandB = -126.58565205881757 },
    { .oper = '%', .operandA = -168.06267619591975, .operandB = -168.06267619591975 },
    { .oper = '^', .operandA = -89.62507013196158, .operandB = 0.31552727790414314 },
    { .oper = '^', .operandA = -435.6326794910422, .operandB = -0.5596086982531079 },
    { .oper = '^', .operandA = -77.15234828127994, .operandB = 55.0 },
    { .oper = '^', .operandA = -122.93451258966626, .operandB = -0.7607795149051053 },
    { .oper = '-', .operandA = -174.37474544684983, .operandB = 319.46165358646 },
    { .oper = '-', .operandA = 242.6846228589452, .operandB = 150.94558247749956 },
    { .oper = '%', .operandA = -91.97685860725163, .operandB = -91.97685860725163 },
    { .oper = '/', .operandA = -294.7693438865663, .operandB = -52.70287127788441 },
    { .oper = '%', .operandA = -351.560219405461, .operandB = -351.560219405461 },
    { .oper = '^', .operandA = -465.15974338843347, .operandB = -0.40664179933223554 },
    { .oper = '+', .operandA = -258.1351789609496, .operandB = -390.0202034371084 },
    { .oper = '/', .operandA = 204.42349844165028, .operandB = -117.75256255255306 },
    { .oper = '^', .operandA = -98.25095127293328, .operandB = 7.0 },
    { .oper = '%', .operandA = -474.9038530330467, .operandB = 474.9038530330467 },
    { .oper = '%', .operandA = -73.02176814262756, .operandB = -73.02176814262756 },
    { .oper = '^', .operandA = -480.8538448137391, .operandB = 0.398084357553655 },
    { .oper = '+', .operandA = -117.61721900987374, .operandB = 267.24754148402667 },
    { .oper = '^', .operandA = -58.78556412923402, .operandB = 99.0 },
    { .oper = '%', .operandA = -396.205850351399, .operandB = 396.205850351399 },
    { .oper = '%', .operandA = -407.6274284098175, .operandB = 407.6274284098175 },
    { .oper = '*', .operandA = 85.76775872766427, .operandB = 207.49908934973303 },
    { .oper = '-', .operandA = 283.78226501609515, .operandB = -188.82556100946846 },
    { .oper = '%', .operandA = 8.433308152348104, .operandB = 441.57763284856094 },
    { .oper = '-', .operandA = -35.139341188183494, .operandB = 34.20370438881059 },
    { .oper = '-', .operandA = -132.261863763708, .operandB = -299.2396390165084 },
    { .oper = '^', .operandA = -134.38546569867637, .operandB = 0.03438468534809336 },
    { .oper = '%', .operandA = -140.75427780247384, .operandB = 140.75427780247384 },
    { .oper = '/', .operandA = 104.73061984631795, .operandB = -133.1371812731221 },
    { .oper = '+', .operandA = 499.6338403383875, .operandB = -375.1493166739683 },
    { .oper = '+', .operandA = 269.8641021273513, .operandB = -294.0303377106679 },
    { .oper = '%', .operandA = -422.3084200316476, .operandB = -422.3084200316476 },
    { .oper = '*', .operandA = -279.6247127256191, .operandB = 328.6297745060897 },
    { .oper = '%', .operandA = -124.65937167062158, .operandB = 124.65937167062158 },
    { .oper = '%', .operandA = -105.44048242243775, .operandB = 105.44048242243775 },
    { .oper = '%', .operandA = -77.94773972339561, .operandB = -304.98322249006816 },
    { .oper = '+', .operandA = -47.20993775675896, .operandB = 398.521418779693 },
    { .oper = '-', .operandA = 184.84387058702941, .operandB = -493.00223583516475 },
    { .oper = '%', .operandA = -442.99759474705166, .operandB = -442.99759474705166 },
    { .oper = '*', .operandA = 242.3322023868459, .operandB = 251.79305000289196 },
    { .oper = '+', .operandA = -357.9762599053308, .operandB = -372.7422103772925 },
    { .oper = '^', .operandA = -71.45563200217433, .operandB = 31.0 },
    { .oper = '%', .operandA = -491.5161540905127, .operandB = -491.5161540905127 },
    { .oper = '%', .operandA = -108.30782083229168, .operandB = -108.30782083229168 },
    { .oper = '/', .operandA = -128.30490570577848, .operandB = -278.0947386342567 },
    { .oper = '/', .operandA = -157.4023143255733, .operandB = 99.58416190365688 },
    { .oper = '^', .operandA = -321.37815854456454, .operandB = -0.6700644558926727 },
    { .oper = '*', .operandA = -23.21240272797729, .operandB = 88.22647796484353 },
    { .oper = '^', .operandA = -140.5686177854314, .operandB = 0.504094949453963 },
    { .oper = '-', .operandA = -28.42074661091243, .operandB = 251.50714906985718 },
    { .oper = '^', .operandA = -296.49167894125173, .operandB = -0.6558120103265221 },
    { .oper = '^', .operandA = -95.9647313235524, .operandB = 81.0 },
    { .oper = '%', .operandA = -251.2374896785937, .operandB = -251.2374896785937 },
    { .oper = '*', .operandA = 401.21956848101377, .operandB = -87.26146617045407 },
    { .oper = '%', .operandA = -430.3914473035836, .operandB = 119.88578472006179 },
    { .oper = '/', .operandA = -47.132232337936614, .operandB = -342.81356188789914 },
    { .oper = '^', .operandA = -410.14172017348744, .operandB = 0.2856737985264768 },
    { .oper = '%', .operandA = -127.63031163891606, .operandB = -258.23138162389216 },
    { .oper = '^', .operandA = -239.80994578905657, .operandB = -0.8304690019239958 },
    { .oper = '%', .operandA = -8.33778312422504, .operandB = -226.18321330090583 },
    { .oper = '%', .operandA = -397.6308129812426, .operandB = 397.6308129812426 },
    { .oper = '*', .operandA = -332.61617123840915, .operandB = -222.22096001700578 },
    { .oper = '^', .operandA = -58.5617119212723, .operandB = 17.0 },
    { .oper = '+', .operandA = 398.1753260403665, .operandB = 470.73716799672025 },
    { .oper = '^', .operandA = -290.6646239819354, .operandB = 0.8688655026214567 },
    { .oper = '*', .operandA = -22.48737271659263, .operandB = 168.1433671953746 },
    { .oper = '%', .operandA = -398.23202773538833, .operandB = -425.0037211349952 },
    { .oper = '^', .operandA = -394.4010662770377, .operandB = -0.24700042992432114 },
    { .oper = '^', .operandA = 25.538095207753155, .operandB = 87.9689525953484 },
    { .oper = '%', .operandA = 106.92708315198797, .operandB = 447.9724127881341 },
    { .oper = '*', .operandA = 300.30140783968034, .operandB = -422.7686180403333 },
    { .oper = '^', .operandA = -320.3751921885789, .operandB = -0.584235550188261 },
    { .oper = '%', .operandA = -90.55138225763498, .operandB = 90.55138225763498 },
    { .oper = '^', .operandA = -198.03096812452316, .operandB = -0.8417203693026956 },
    { .oper = '^', .operandA = -18.02709984794343, .operandB = 0.5363583337842031 },
    { .oper = '%', .operandA = -209.95216426976003, .operandB = -209.95216426976003 },
    { .oper = '/', .operandA = 166.84199687106184, .operandB = 71.80435368282588 },
    { .oper = '*', .operandA = -144.03054969402353, .operandB = -8.14033616381738 },
    { .oper = '^', .operandA = 16.331368287087525, .operandB = 9.440282839262771 },
    { .oper = '-', .operandA = 318.9528083071659, .operandB = -100.2682079162638 },
    { .oper = '^', .operandA = -430.59065631914586, .operandB = -0.0614408665561712 },
    { .oper = '^', .operandA = -177.70562468096662, .operandB = -0.5100801911793171 },
    { .oper = '^', .operandA = -331.56668566438026, .operandB = 0.08585569734322762 },
    { .oper = '^', .operandA = 98.51242110201838, .operandB = 53.26161118637498 },
    { .oper = '+', .operandA = 271.9852320811567, .operandB = -257.86831663651935 },
    { .oper = '+', .operandA = -264.09023048365384, .operandB = -406.7189764827539 },
    { .oper = '^', .operandA = -332.619817355589, .operandB = 0.8074796214553475 },
    { .oper = '%', .operandA = -305.16796113315735, .operandB = 264.9923843230281 },
    { .oper = '%', .operandA = -209.28426436734298, .operandB = 209.28426436734298 },
    { .oper = '-', .operandA = -489.5331804689474, .operandB = 45.55528389702715 },
    { .oper = '^', .operandA = -190.353105930031, .operandB = 0.9279065359789931 },
    { .oper = '+', .operandA = 261.2531827317107, .operandB = -286.25008356059067 },
    { .oper = '/', .operandA = -211.79959356497943, .operandB = 472.5204320491 },
    { .oper = '*', .operandA = -54.776654536618935, .operandB = 403.0065674847991 },
    { .oper = '^', .operandA = -403.0929746531724, .operandB = -0.27798097231124475 },
    { .oper = '*', .operandA = 163.3847487724289, .operandB = -407.804988695334 },
    { .oper = '%', .operandA = -97.13469326338902, .operandB = 97.13469326338902 },
    { .oper = '/', .operandA = -455.2966453958188, .operandB = -95.37703832120013 },
    { .oper = '^', .operandA = -342.3548946789988, .operandB = -0.11674083923447798 },
    { .oper = '+', .operandA = -320.33933190409994, .operandB = -430.07852553170335 },
    { .oper = '-', .operandA = -458.4787433605626, .operandB = -60.98519243444821 },
    { .oper = '-', .operandA = 323.4194767543704, .operandB = -98.03607228783517 },
    { .oper = '-', .operandA = 255.0762587444524, .operandB = -17.364801771449493 },
    { .oper = '*', .operandA = -159.60719756439465, .operandB = 249.69446119182282 },
    { .oper = '*', .operandA = 486.1762963487778, .operandB = 336.85999310445004 },
    { .oper = '^', .operandA = -475.2905250578201, .operandB = 0.8504359483715576 },
    { .oper = '%', .operandA = -36.800358736233775, .operandB = -36.800358736233775 },
    { .oper = '%', .operandA = -182.34819230984144, .operandB = 182.34819230984144 },
    { .oper = '-', .operandA = 467.7766551403014, .operandB = -441.2925115214279 },
    { .oper = '*', .operandA = 266.419417360063, .operandB = -63.975418070567514 },
    { .oper = '/', .operandA = -304.112947522169, .operandB = -461.3144461217887 },
    { .oper = '%', .operandA = -365.5990592247167, .operandB = -365.5990592247167 },
    { .oper = '^', .operandA = -297.4699378784764, .operandB = -0.5773872658138688 },
    { .oper = '+', .operandA = 307.3514457033476, .operandB = -25.710846038051045 },
    { .oper = '^', .operandA = -71.69747272483716, .operandB = 73.0 },
    { .oper = '%', .operandA = -326.5610378443252, .operandB = -326.5610378443252 },
    { .oper = '%', .operandA = -168.79302049664818, .operandB = 168.79302049664818 },
    { .oper = '+', .operandA = 433.4071146420388, .operandB = -70.66991804550861 },
    { .oper = '^', .operandA = -81.77515455506939, .operandB = 0.3091059163191576 },
    { .oper = '/', .operandA = 445.18200758142336, .operandB = -320.6557865724515 },
    { .oper = '^', .operandA = -91.74842333494809, .operandB = 0.06717543061049813 },
    { .oper = '%', .operandA = 259.1436558203844, .operandB = -165.99028083558932 },
    { .oper = '%', .operandA = 13.013689110180962, .operandB = -436.93077260683435 },
    { .oper = '/', .operandA = 332.8834822252668, .operandB = 168.92096765873487 },
    { .oper = '^', .operandA = -335.00845097620805, .operandB = 0.8090072521240703 },
    { .oper = '-', .operandA = 119.49150342245935, .operandB = 452.1997536582252 },
    { .oper = '/', .operandA = -33.61544529448537, .operandB = 226.6144682430429 },
    { .oper = '%', .operandA = 368.8840503941358, .operandB = 358.98232442718097 },
    { .oper = '*', .operandA = -105.46763349869747, .operandB = -301.9189918381502 },
    { .oper = '/', .operandA = 270.7856335602969, .operandB = 86.78310539196082 },
    { .oper = '%', .operandA = -79.23893586760383, .operandB = -79.23893586760383 },
    { .oper = '*', .operandA = 65.37616989637559, .operandB = 250.58242149261855 },
    { .oper = '^', .operandA = -247.78940287062306, .operandB = -0.5764870534825064 },
    { .oper = '^', .operandA = -80.43263965418926, .operandB = 97.0 },
    { .oper = '^', .operandA = -229.78564334433926, .operandB = 0.5231194333156883 },
    { .oper = '-', .operandA = -291.9159102748514, .operandB = -117.13039652384924 },
    { .oper = '^', .operandA = -460.19160518211, .operandB = 0.7310191131580686 },
    { .oper = '%', .operandA = -287.141533578852, .operandB = -287.141533578852 },
    { .oper = '%', .operandA = -165.09968228713274, .operandB = -165.09968228713274 },
    { .oper = '*', .operandA = 27.703680314375788, .operandB = -71.75522123743758 },
    { .oper = '%', .operandA = -166.2734558827129, .operandB = -166.2734558827129 },
    { .oper = '%', .operandA = 318.67029200471404, .operandB = 457.76994378805307 },
    { .oper = '^', .operandA = -350.8241982853795, .operandB = 0.5284536581380765 },
    { .oper = '%', .operandA = 65.16561987924581, .operandB = 138.0752858271028 },
    { .oper = '+', .operandA = -81.47431401565927, .operandB = 101.82753628117996 },
    { .oper = '/', .operandA = 346.83673198764984, .operandB = -472.5983232778733 },
    { .oper = '-', .operandA = -495.31389546023195, .operandB = -229.065771643326 },
    { .oper = '%', .operandA = -205.6747798441199, .operandB = -205.6747798441199 },
    { .oper = '%', .operandA = -267.1057892244319, .operandB = 267.1057892244319 },
    { .oper = '+', .operandA = 329.258582041222, .operandB = -216.9752706836806 },
    { .oper = '+', .operandA = -377.81697277722105, .operandB = -397.27149085255155 },
    { .oper = '%', .operandA = -44.50526642739289, .operandB = -44.50526642739289 },
    { .oper = '-', .operandA = 239.7707880974558, .operandB = 363.26726520228476 },
    { .oper = '%', .operandA = -175.55768138326854, .operandB = -175.55768138326854 },
    { .oper = '^', .operandA = -212.4513869895544, .operandB = 0.2278950565833462 },
    { .oper = '%', .operandA = 68.32948123433016, .operandB = -258.72757031642084 },
    { .oper = '*', .operandA = 496.1765032584909, .operandB = 85.08382046982376 },
    { .oper = '+', .operandA = -236.09436926152063, .operandB = 105.11519168309314 },
    { .oper = '*', .operandA = -348.9908893855387, .operandB = -84.33677295878681 },
    { .oper = '-', .operandA = -470.7916526905721, .operandB = 407.7199915901973 },
    { .oper = '^', .operandA = -346.46499330676005, .operandB = 0.014204113872082536 },
    { .oper = '%', .operandA = -402.6366504242033, .operandB = 402.6366504242033 },
    { .oper = '%', .operandA = -269.3054182939108, .operandB = -269.3054182939108 },
    { .oper = '%', .operandA = 306.402809193317, .operandB = 344.88248105169293 },
    { .oper = '%', .operandA = -202.00043869335062, .operandB = 202.00043869335062 },
    { .oper = '/', .operandA = -55.463612339269105, .operandB = 269.633308481816 },
    { .oper = '%', .operandA = -416.4903044922913, .operandB = -416.4903044922913 },
    { .oper = '-', .operandA = 64.5346592396478, .operandB = 16.961496678724302 },
    { .oper = '%', .operandA = 470.5512565280966, .operandB = 63.93156807293724 },
    { .oper = '+', .operandA = 175.46907702424858, .operandB = 202.97895801902234 },
    { .oper = '^', .operandA = -344.39457674456446, .operandB = 0.32992936167161324 },
    { .oper = '%', .operandA = -243.31049466164495, .operandB = 243.31049466164495 },
    { .oper = '^', .operandA = 3.6406181417831025, .operandB = 82.06735032439116 },
    { .oper = '-', .operandA = 218.29791798938254, .operandB = 428.6472666309246 },
    { .oper = '^', .operandA = -259.49025818337674, .operandB = -0.6695647693798996 },
    { .oper = '%', .operandA = -73.94952201977777, .operandB = 73.94952201977777 },
    { .oper = '^', .operandA = -338.6706419714745, .operandB = -0.3777617187065907 },
    { .oper = '^', .operandA = -467.82569953535057, .operandB = 0.20425467755165094 },
    { .oper = '%', .operandA = -222.66667298517962, .operandB = -222.66667298517962 },
    { .oper = '%', .operandA = -379.81983626059576, .operandB = -379.81983626059576 },
    { .oper = '%', .operandA = -440.7643880192924, .operandB = -440.7643880192924 },
    { .oper = '/', .operandA = -301.309663417501, .operandB = 273.74302504825573 },
    { .oper = '%', .operandA = -371.8141950545257, .operandB = -345.4138044144127 },
    { .oper = '-', .operandA = 404.1803168174017, .operandB = 6.694178373420812 },
    { .oper = '*', .operandA = 102.18040666180548, .operandB = 377.03749467852606 },
    { .oper = '%', .operandA = 30.648157313301, .operandB = -338.5609672152443 },
    { .oper = '/', .operandA = -104.66377600898636, .operandB = -16.893437057484164 },
    { .oper = '%', .operandA = -429.94945159339005, .operandB = -429.94945159339005 },
    { .oper = '^', .operandA = -444.67634343240104, .operandB = -0.674247986309302 },
    { .oper = '/', .operandA = -139.63148412764514, .operandB = -196.8664533654221 },
    { .oper = '%', .operandA = -17.521684620655897, .operandB = -17.521684620655897 },
    { .oper = '^', .operandA = 9.3482479857215, .operandB = 27.067917000081785 },
    { .oper = '/', .operandA = 68.28691457053867, .operandB = 403.94153274523444 },
    { .oper = '^', .operandA = 75.84886038832583, .operandB = 49.00829075342995 },
    { .oper = '-', .operandA = 207.58246437336072, .operandB = 26.387860963310914 },
    { .oper = '^', .operandA = -452.9766678962322, .operandB = -0.14707826177868677 },
    { .oper = '^', .operandA = -484.702468340655, .operandB = 0.4348512994528775 },
    { .oper = '+', .operandA = 48.46351179981991, .operandB = 176.83590871237266 },
    { .oper = '+', .operandA = -44.40364055737342, .operandB = -140.99273173226345 },
    { .oper = '+', .operandA = 491.125447744961, .operandB = -132.93236056436973 },
    { .oper = '%', .operandA = -401.950502789964, .operandB = 401.950502789964 },
    { .oper = '%', .operandA = 95.61728073065797, .operandB = -211.69015022606754 },
    { .oper = '*', .operandA = 283.00110122703336, .operandB = 229.05477981386753 },
    { .oper = '^', .operandA = -93.11166355230489, .operandB = 67.0 },
    { .oper = '^', .operandA = -363.2919677291165, .operandB = 0.6544511415975767 },
    { .oper = '-', .operandA = -14.563905621013646, .operandB = -295.435280853623 },
    { .oper = '%', .operandA = -493.4958365346321, .operandB = 493.4958365346321 },
    { .oper = '^', .operandA = -16.39177970702201, .operandB = 89.0 },
    { .oper = '^', .operandA = -474.0240219161051, .operandB = 0.40969599790513755 },
    { .oper = '^', .operandA = -79.55270502953854, .operandB = 69.0 },
    { .oper = '/', .operandA = 53.95071213569338, .operandB = 383.22884109825327 },
    { .oper = '%', .operandA = -93.79417632230607, .operandB = 93.79417632230607 },
    { .oper = '%', .operandA = -463.28804367436976, .operandB = 463.28804367436976 },
    { .oper = '%', .operandA = 45.187208986415385, .operandB = -39.86790896724335 },
    { .oper = '-', .operandA = 202.91999675072395, .operandB = -324.16403558562024 },
    { .oper = '^', .operandA = -194.69288639710336, .operandB = -0.5776762313604342 },
    { .oper = '-', .operandA = -330.18369151864067, .operandB = -297.88413870519815 },
    { .oper = '^', .operandA = -1.5054716846414906, .operandB = -0.7178150526698348 },
    { .oper = '^', .operandA = -96.60808659377845, .operandB = 41.0 },
    { .oper = '%', .operandA = -149.6662441491185, .operandB = -149.6662441491185 },
    { .oper = '%', .operandA = -367.147354687935, .operandB = -367.147354687935 },
    { .oper = '^', .operandA = 12.005742079583781, .operandB = 29.741171723996903 },
    { .oper = '/', .operandA = -237.2787164054493, .operandB = 255.70493312340375 },
    { .oper = '*', .operandA = -482.697597612631, .operandB = -454.73524006506915 },
    { .oper = '^', .operandA = 77.73409264992017, .operandB = 30.846980855171264 },
    { .oper = '^', .operandA = 66.66469898603206, .operandB = 62.07260194648222 },
    { .oper = '/', .operandA = 344.399108084358, .operandB = -330.9725139372987 },
    { .oper = '^', .operandA = -83.51826090519724, .operandB = 75.0 },
    { .oper = '+', .operandA = -67.66823474154336, .operandB = -11.916307481130502 },
    { .oper = '*', .operandA = -359.4430859114567, .operandB = 408.8380987523959 },
    { .oper = '^', .operandA = -53.98972277590986, .operandB = 61.0 },
    { .oper = '/', .operandA = -272.64648754258656, .operandB = -52.3894271169666 },
    { .oper = '*', .operandA = 370.61271052880625, .operandB = 184.7601646528367 },
    { .oper = '%', .operandA = -361.9152834419255, .operandB = 361.9152834419255 },
    { .oper = '-', .operandA = -467.13697375786256, .operandB = -203.26472354297232 },
    { .oper = '-', .operandA = 278.3826603132402, .operandB = 415.53019971675326 },
    { .oper = '^', .operandA = -301.06746353163766, .operandB = 0.8291233788823997 },
    { .oper = '%', .operandA = 472.3230422807608, .operandB = 81.34762990120385 },
    { .oper = '%', .operandA = -107.60194555366392, .operandB = 107.60194555366392 },
    { .oper = '^', .operandA = -310.4072515630693, .operandB = 0.6259231486837773 },
    { .oper = '^', .operandA = -9.486913237689354, .operandB = 0.7907695910004302 },
    { .oper = '%', .operandA = -120.29655579972575, .operandB = -120.29655579972575 },
    { .oper = '^', .operandA = -163.37466737228152, .operandB = 0.8650593011671992 },
    { .oper = '%', .operandA = -156.71726950454084, .operandB = 156.71726950454084 },
    { .oper = '^', .operandA = -64.6105107425794, .operandB = -0.09947667609772903 },
    { .oper = '^', .operandA = 63.50062738464233, .operandB = 33.98324540312984 },
    { .oper = '%', .operandA = 386.12870817258863, .operandB = -107.06830519591057 },
    { .oper = '%', .operandA = -380.73167945944573, .operandB = -380.73167945944573 },
    { .oper = '+', .operandA = 159.0706948979946, .operandB = 250.32090292991245 },
    { .oper = '^', .operandA = -4.873245128917736, .operandB = -0.37441779072582015 },
    { .oper = '+', .operandA = 2.458901363309735, .operandB = 161.10526065631393 },
    { .oper = '%', .operandA = -41.19941306413616, .operandB = -41.19941306413616 },
    { .oper = '^', .operandA = -496.0770737355603, .operandB = -0.8111795106414499 },
    { .oper = '^', .operandA = -38.61374487658282, .operandB = 39.0 },
    { .oper = '/', .operandA = 187.61851812098791, .operandB = -303.9626655156481 },
    { .oper = '*', .operandA = 151.7987367885288, .operandB = 167.64012410421253 },
    { .oper = '%', .operandA = -128.934289153541, .operandB = 87.08867897625782 },
    { .oper = '/', .operandA = 489.4137106489145, .operandB = 196.582231326621 },
    { .oper = '/', .operandA = 313.90386514940644, .operandB = 307.5119180799759 },
    { .oper = '*', .operandA = -318.7807743336529, .operandB = 106.47352567841517 },
    { .oper = '%', .operandA = 244.98686890869726, .operandB = 19.760450548264885 },
    { .oper = '/', .operandA = -218.38102535544033, .operandB = 56.316537562079475 },
    { .oper = '/', .operandA = -321.4690899762336, .operandB = 471.99875969680625 },
    { .oper = '%', .operandA = -468.8507521901163, .operandB = -468.8507521901163 },
    { .oper = '+', .operandA = -230.19891053585417, .operandB = -454.97604953002866 },
    { .oper = '%', .operandA = -413.0430009119941, .operandB = -10.946703544069123 },
    { .oper = '^', .operandA = -51.3107384610953, .operandB = 0.9548851577999304 },
    { .oper = '%', .operandA = -377.2368844087873, .operandB = 377.2368844087873 },
    { .oper = '%', .operandA = -103.70165646503298, .operandB = -103.70165646503298 },
    { .oper = '%', .operandA = 285.92254208579675, .operandB = -378.089856913595 },
    { .oper = '%', .operandA = -287.4060970240897, .operandB = -407.32344177774627 },
    { .oper = '-', .operandA = 443.2396196174817, .operandB = -25.4607369662653 },
    { .oper = '^', .operandA = -125.3965698755341, .operandB = -0.22820067602803573 },
    { .oper = '%', .operandA = -239.3594747454114, .operandB = -239.3594747454114 },
    { .oper = '%', .operandA = -4.736105526029322, .operandB = -4.736105526029322 },
    { .oper = '%', .operandA = 58.03201117994729, .operandB = -290.0824981866179 },
    { .oper = '^', .operandA = -93.08388076635198, .operandB = 77.0 },
    { .oper = '^', .operandA = -29.631595137895175, .operandB = 23.0 },
    { .oper = '%', .operandA = -166.0881694563761, .operandB = 166.0881694563761 },
    { .oper = '/', .operandA = 463.89950728476845, .operandB = 332.1402224867336 },
    { .oper = '%', .operandA = -112.05838397360995, .operandB = -112.05838397360995 },
    { .oper = '-', .operandA = -131.18306961482085, .operandB = -224.193419050567 },
    { .oper = '%', .operandA = -358.31390085291673, .operandB = -269.1094759160254 },
    { .oper = '%', .operandA = -160.9933645098241, .operandB = 160.9933645098241 },
    { .oper = '%', .operandA = -126.55669891797004, .operandB = 360.69228913508084 },
    { .oper = '-', .operandA = -305.10959125407066, .operandB = 308.4690271754432 },
    { .oper = '%', .operandA = 352.83615271777626, .operandB = -191.47128240160947 },
    { .oper = '+', .operandA = 89.61508900847014, .operandB = 89.1234497989733 },
    { .oper = '+', .operandA = -203.14813813217648, .operandB = 117.57276042687715 },
    { .oper = '^', .operandA = 66.37433504049558, .operandB = 14.781441588664144 },
    { .oper = '^', .operandA = -39.73744088699632, .operandB = 55.0 },
    { .oper = '/', .operandA = 443.92105349183987, .operandB = 53.74338477053027 },
    { .oper = '/', .operandA = -0.4580954923237641, .operandB = -214.804781136109 }
  };
  char encflag[] = { 
    75,
    195,
    225,
    1,
    0,
    185,
    238,
    16,
    238,
    75,
    240,
    164,
    120,
    33,
    56,
    203,
    234,
    42,
    33,
    107,
    206,
    131,
    70,
    232,
    65,
    167,
    140,
    44,
    9,
    207,
    245,
    160,
    161,
    114,
    39,
    8,
    96,
    40,
    169,
    32,
    102,
    179,
    171,
    53,
    164,
    233
  };

  /* Length checks */
  int len_encflag = sizeof(encflag) / sizeof(encflag[0]);
  int len_operations = sizeof(operations) / sizeof(operation_t);
  // if ((len_encflag * 8) != len_operations) {
  //   printf("Length of operations did not match encrypted flag: %d, %d", len_operations, len_encflag);
  //   return -1;
  // }

  /* Input loop - ensure that operations are entered correctly in order, reset if incorrect */
  double operation_results[len_operations];
  printf("Welcome to the fastest, most optimized calculator ever!\n");
  printf("Example usage:\n");
  printf("  Add:       1 + 2\n");
  printf("  Subtract:  10 - 24\n");
  printf("  Multiply:  34 * 8\n");
  printf("  Divide:    20 / 3\n");
  printf("  Modulo:    60 %% 9\n");
  printf("  Exponent:  2 ^ 12\n\n");
  printf("If you enter the correct secret operation, I might decrypt the flag for you! ^-^\n\n");

  while (true) {
    char oper;
    double operandA, operandB;
    printf("Enter your operation: ");
    while (scanf(" %lf %c %lf", &operandA, &oper, &operandB) != 3) {
      while (getchar() != '\n');
      printf("Enter your operation: ");
    }
    if (oper != '+' && oper != '-' && oper != '*' && oper != '/' && oper != '%' && oper != '^') {
      printf("Invalid operation!\n");
      continue;
    }
    double result = calculate((operation_t) { .oper = oper, .operandA = operandA, .operandB = operandB });
    printf("Result: %lf\n", result);
    if (result == 8573.8567) {
      printf("\nCorrect! Attempting to decrypt the flag...\n");
      /* Make a copy of encflag for use in decryption */
      char decflag[len_encflag];
      memcpy(decflag, encflag, len_encflag);
      /* Decrypt the flag using the stored operations array */
      int num_bitflips = 0;
      for (int i = 0; i < len_operations; i++) {
        if (gauntlet(calculate(operations[i]))) {
          /* Flip bit */
          int byte_idx = i / 8;
          int bit_idx = i % 8;
          decflag[byte_idx] ^= (1 << (7 - bit_idx));
          num_bitflips++;
        }
      }
      printf("I calculated %d operations, tested each result in the gauntlet, and flipped %d bits in the encrypted flag!\n", len_operations, num_bitflips);
      printf("Here is your decrypted flag:\n\n");
      printf("%s\n\n", decflag);
    }
  }
}

double calculate(operation_t o) {
  double calc = 0.0;
  switch (o.oper) {
    case ADD:
      calc = o.operandA + o.operandB;
      break;
    case SUB:
      calc = o.operandA - o.operandB;
      break;
    case MUL:
      calc = o.operandA * o.operandB;
      break;
    case DIV:
      calc = o.operandA / o.operandB;
      break;
    case MOD:
      calc = fmod(o.operandA, o.operandB);
      break;
    case POW:
      calc = pow(o.operandA, o.operandB);
      break;
  }
  return calc;
}

bool gauntlet(double result) {
  return (isNegative(result) || isNotNumber(result) || isInfinity(result));
}