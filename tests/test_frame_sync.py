import logging

import numpy as np
import sksdr

_log = logging.getLogger(__name__)

def test_frame_sync():
    threshold = 8.0
    frame_size = 100
    mod = sksdr.QPSK
    psk = sksdr.PSKModulator(mod, [0, 1, 3, 2], phase_offset=np.pi/4)
    preamble = np.repeat(sksdr.UNIPOLAR_BARKER_SEQ[13], 2)
    n_symbols = len(preamble) // mod.bits_per_symbol
    modulated_preamble = np.empty(n_symbols, dtype=complex)
    psk.modulate(preamble, modulated_preamble)
    frame_sync = sksdr.PreambleSync(modulated_preamble, threshold, frame_size)

    # This physical frame contains the preamble but not a full logical frame
    in_frame = np.array([
        0.                    +0.j                    ,
        0.00045504183194606325-0.00013286298404358807j,
        0.00019239095131405592+0.00046127169953936043j,
       -0.000625503991047037  +0.0013038937523887353j ,
       -0.0021936594410494783 +0.0020046825330427547j ,
       -0.01367376131356991   -0.021574596884554223j  ,
       -0.17058869276311073   +0.09600779050934206j   ,
        0.03646583859244239   +0.0025241528605583255j ,
       -0.08850339571545747   -0.027726520041101377j  ,
       -0.11057768118209219   -0.06468349249557807j   ,
       -0.12911549549201634   +0.7071900262328085j    ,
       -0.03391739107323899   +1.6829837670074899j    ,
        0.0730280636152674    +1.285450342500413j     ,
       -0.10435923504930421   +1.426348869730055j     ,
       -0.6218611665331598    +1.9499406674304791j    ,
        0.10065109406522066   -0.026554470776619765j  ,
        0.6493039828099624    -2.3346240087232j       ,
       -0.19271052068182715   -0.34918350764655787j   ,
       -0.2970119471026417    +2.292105983578127j     ,
        0.5540482169449233    -0.09433480707899503j   ,
       -0.7811399312132625    -0.06478396423613934j   ,
        0.3834154489845994    +0.12799825630160586j   ,
       -0.2352063557547754    -0.4523947814836018j    ,
        0.8216814690993856    +1.995342062734069j     ,
        1.2139192546756332    -1.058158900986729j     ,
        1.215030883309646     -0.8959299829209432j    ,
        0.6887763494158518    +1.1683408097505774j    ,
       -0.5875453065986004    +1.6642551304789044j    ,
       -0.8899873372384255    +0.6375132470876778j    ,
       -0.9179215160609208    -1.2354533170565436j    ,
        0.9490698799067947    -0.6404847492988661j    ,
        0.7737630460671475    +0.6956987105583854j    ,
       -0.5719460995733634    +1.486763094143802j     ,
       -0.6349416929057569    +0.3633458029168643j    ,
       -1.2899645660118655    -0.3301512578272602j    ,
       -1.4657833023932099    -0.12692908684361412j   ,
       -0.32196193654692634   -0.8129849127578831j    ,
        1.0489173261254594    -0.6604507000328658j    ,
        0.4306885490623712    +1.0964034604323345j    ,
       -0.8236862890365719    +0.6486884867571237j    ,
       -1.1064454630799543    -0.5176498486136625j    ,
       -0.6972150836904739    +0.4299099573179752j    ,
       -0.8458781118252996    +0.20366973720609016j   ,
        0.09450462361437995   -0.10579300291497379j   ,
        0.5843578754656225    +0.7250883727845516j    ,
       -0.8795803056850817    +0.971720533162076j     ,
        0.4667687591685125    +0.8978517228622711j    ,
        0.04797702782997082   -0.5476726466574942j    ,
       -0.2665074162740675    +0.0752324029980533j    ,
        0.7068066436868098    +0.650960715856507j     ,
       -0.7429125098381866    +0.24191988501507516j   ,
       -0.941663626641849     +0.0440211602325864j    ,
        0.4527711246097275    +0.7802147434407857j    ,
        1.2670951866750226    +0.3826819182786586j    ,
       -0.04084747240977166   -0.15934453115125916j   ,
       -0.31068342668697924   -0.021919010879470957j  ,
        0.3793153986909309    +0.7286305796586262j    ,
       -0.09135633626935058   +0.2521520500788982j    ,
        0.38283036127394887   -1.0493637043353699j    ,
        0.5322562208678986    -0.9111097091371199j    ,
       -0.033294863745490844  -0.1108967923622809j    ,
        0.13886509258616503   +1.129373998665531j     ,
        0.22361860129475364   +0.4133611523184811j    ,
        0.06951263978130012   +0.13609694096976044j   ,
       -0.13632414329378406   -0.8992125989692281j    ,
       -0.9082516535087548    -0.3638029850828808j    ,
       -0.9584519354416745    +0.16299188920087965j   ,
       -0.6315929144686548    +0.14895940574606037j   ,
       -0.18897523484134549   -0.1380777946700359j    ,
        0.3285101718305785    +0.8355533156763867j    ,
        0.025584559886926095  +0.2551663188672287j    ,
        0.276747636015355     -0.9185318795454923j    ,
       -0.8586487391863051    -0.5999524372215721j    ,
       -0.8432705205216467    +0.07883221989846587j   ,
       -0.670120673850388     +0.1664458754050091j    ,
       -0.2153889438747541    -0.3341896866248936j    ,
        1.1927974566730042    +0.5323478621394402j    ,
       -0.014937271528199604  +0.7108124053339271j    ,
       -0.2854205967030613    +0.5170402014875659j    ,
        0.5202050645229509    -1.0173267485025104j    ,
        0.553480843182039     +0.01581386426130595j   ,
        0.7541310352188072    +0.22838458560698582j   ,
       -0.06958673486291303   -0.8615889027310051j    ,
       -0.9718831879416943    -0.7162300775430247j    ,
        0.004568380942336109  +0.048292195108247504j  ,
        0.4913536046586128    -0.10429272272566664j   ,
       -1.1172784751887526    -0.15026192887765816j   ,
        0.060494033128144775  +1.0224593102416586j    ,
        1.0421186402335338    -0.1495402234413237j    ,
       -0.34175882598337914   -0.9976375763089045j    ,
       -0.4418783892916689    +0.09606248542670624j   ,
        0.8502915482556148    +0.6278795516831366j    ,
        1.0393000586524352    -0.17934661968016588j   ,
       -0.4428318071623186    -0.08185379169154638j   ,
       -0.03840219211871326   +0.3806733800901507j    ,
        0.7740820608781789    -0.924384433059227j     ,
       -0.06167217403691509   -0.9314402414595253j    ,
       -0.11400934942587365   -0.48497235537363326j   ,
       -0.0028636887583518567 -1.1221186543315091j    ,
       -0.07270280692867603   +0.07124285584203287j   ])

    # out_frame is None, since the frame is still incomplete
    out_frame = np.empty(frame_size, dtype=complex)
    frame_sync(in_frame, out_frame)

    # This physical frame contains the rest of the 1st logical frame and a the
    # beginning of the 2nd logical frame
    in_frame = np.array([
        0.28073051483508893 +0.5857275682614242j ,
       -0.654984543856036   +0.8354231785661262j ,
       -0.5187261917509268  +0.6019799926334745j ,
       -0.4473579551406935  +0.17295971347710265j,
       -0.9284783656351782  -0.8335198899206268j ,
       -0.31778182883427525 -0.6188191745546093j ,
        0.80962405464884    -0.8877716829190442j ,
       -0.28078718449479595 -0.17295680174386513j,
       -0.011206013797797343+1.0808443743319494j ,
        0.12407651502056877 +0.5625172473669444j ,
       -0.6142909156079297  +0.7773840695944384j ,
       -0.6710531715907438  +0.5945142184192249j ,
       -0.5834460468911354  +0.41656593979155493j,
       -0.6729390212467068  +0.6700939077171245j ,
       -0.8214139036871554  +0.7802880248446878j ,
       -0.2155276529422869  +0.29249064566307753j,
        0.9269287887010436  -0.9050455341184249j ,
        0.10585375397194657 -0.3102853414251855j ,
       -0.8882959323068325  +1.0833177395510702j ,
        0.057983160647565216+0.27806455381867984j,
       -0.03508745598777968 -0.29643175301297015j,
       -0.06392578257401182 +0.3112945607463916j ,
       -0.0635600116765016  -0.6176005128349288j ,
       -0.802798011054973   +1.1396665515914126j ,
       -0.6787526046062744  +0.01135187115260156j,
       -0.5037163832578483  -0.23598232359451565j,
        1.3328163314880277  +0.4444263712555946j ,
        0.05223689641654251 -0.8703145215844331j ,
       -0.8121020750298964  -0.6070619989808789j ,
        0.0972166881012666  -0.14100526069993038j,
        0.4764989867741247  +0.7113685819606328j ,
       -0.33120603511743735 +0.9664683674540779j ,
        0.19787849847061306 +0.44142267554398457j,
       -0.3196566628371983  +0.7957066074405696j ,
        0.2683656710413588  +0.40801003056414686j,
       -0.940858559957481   +0.22377571191792067j,
       -0.15251242687712027 -0.3965656875219443j ,
        0.4744668608301966  +0.7977026193312929j ,
       -0.5965620683362711  +1.1161498849878482j ,
        0.36717393119353253 +0.20894916315693188j,
       -0.5974335231535834  -0.18482905428748525j,
        0.5383433498865274  +0.34405283019515154j,
       -1.029033877962315   -1.0564319600144434j ,
       -0.11311093966297024 -0.9537622818794008j ,
        0.8817680759259472  -0.1993280730072458j ,
        0.8336673333938899  +0.9135570051803444j ,
        0.4407767620788784  +0.7841712943669024j ,
        0.5523708979845983  +0.7105481833657441j ,
        0.8560229502380826  +0.5379490517597526j ,
        0.3861270967091964  -0.5576854557361914j ,
       -1.0745647748838807  +1.0048555441021574j ,
       -0.4466090805472217  +0.756952470866884j  ,
        0.5804683922276797  +0.37846852071084547j,
       -0.7711509449206237  +0.741431934256432j  ,
        0.5288449842400899  +0.7170755633356042j ,
        0.9435524279782556  +0.3748950212911027j ,
        0.18937514299939107 -0.6971849738101608j ,
       -0.5386062547642435  +0.7666886506940289j ,
        0.562117420823954   +0.4433003205122375j ,
       -0.7936318066366325  -0.8617546246731637j ,
       -0.7510034630406679  -0.5027966610939557j ,
       -0.6193497711489593  +0.34421301637735446j,
       -0.5627617523096998  -0.9194027725867163j ,
       -0.1345693807484186  -0.711927378377345j  ,
        0.1880444386945353  -0.3481431634874669j ,
       -0.5826374407598742  +0.45965823475601414j,
        0.6534801216374374  -0.42693678493373344j,
        0.3467554585535072  +0.635991956638187j  ,
       -0.7405166697691511  -1.1467259181147684j ,
       -0.6746989726409601  -0.6926806043840299j ,
       -0.12899899696190606 -0.6568914943583638j ,
        0.33561367226091554 -0.3466378019656395j ,
       -0.5426671695334722  +0.42891797632856443j,
        1.0348860771495911  -0.5593048234647113j ,
        0.14222058143695357 +0.5588080554499086j ,
       -0.6815819956638515  -0.7298905876888243j ,
        0.9174985259028184  -0.5785289960112789j ,
        0.7296999831378729  -0.328725816545086j  ,
        0.6426792371999372  +0.8657476283415609j ,
        0.4667930085491786  -0.5768119063417525j ,
        0.6219177743503925  +1.0076755375017061j ,
        0.4429261055372874  +0.4356674068572195j ,
       -0.6852888513872111  -0.8701937551282325j ,
        0.6918550791493947  +1.0119858045571877j ,
        0.6267489891354989  +0.6768859485402046j ,
        0.992640129888497   -0.558047591146347j  ,
        0.7091773023454319  -0.7745409688838162j ,
       -0.8956866725982955  -0.6798477843960647j ,
       -0.917360901361376   +0.5645819143452024j ,
       -0.6444612674511792  +0.5238684135347551j ,
        0.43948000723826325 +0.5040213505908655j ,
       -0.6298680692434044  -0.666642343818425j  ,
        0.4558994006359583  +0.5230278658719532j ,
       -0.6131723497501841  -0.9460596102569088j ,
       -0.35845114474150397 -0.6194554074548885j ,
        0.6879750157100425  -0.7904699821138752j ,
       -0.5278349597625425  -0.6091323218503174j ,
        0.523958841561116   +0.8692148665194882j ,
       -0.7725834620499579  +0.5007474087373552j ,
       -0.3959172942573768  -0.7799395989515291j ])

    expected_frame = np.array([
        -0.03391739107323899  +1.6829837670074899j  ,
        0.0730280636152674   +1.285450342500413j   ,
       -0.10435923504930421  +1.426348869730055j   ,
       -0.6218611665331598   +1.9499406674304791j  ,
        0.10065109406522066  -0.026554470776619765j,
        0.6493039828099624   -2.3346240087232j     ,
       -0.19271052068182715  -0.34918350764655787j ,
       -0.2970119471026417   +2.292105983578127j   ,
        0.5540482169449233   -0.09433480707899503j ,
       -0.7811399312132625   -0.06478396423613934j ,
        0.3834154489845994   +0.12799825630160586j ,
       -0.2352063557547754   -0.4523947814836018j  ,
        0.8216814690993856   +1.995342062734069j   ,
        1.2139192546756332   -1.058158900986729j   ,
        1.215030883309646    -0.8959299829209432j  ,
        0.6887763494158518   +1.1683408097505774j  ,
       -0.5875453065986004   +1.6642551304789044j  ,
       -0.8899873372384255   +0.6375132470876778j  ,
       -0.9179215160609208   -1.2354533170565436j  ,
        0.9490698799067947   -0.6404847492988661j  ,
        0.7737630460671475   +0.6956987105583854j  ,
       -0.5719460995733634   +1.486763094143802j   ,
       -0.6349416929057569   +0.3633458029168643j  ,
       -1.2899645660118655   -0.3301512578272602j  ,
       -1.4657833023932099   -0.12692908684361412j ,
       -0.32196193654692634  -0.8129849127578831j  ,
        1.0489173261254594   -0.6604507000328658j  ,
        0.4306885490623712   +1.0964034604323345j  ,
       -0.8236862890365719   +0.6486884867571237j  ,
       -1.1064454630799543   -0.5176498486136625j  ,
       -0.6972150836904739   +0.4299099573179752j  ,
       -0.8458781118252996   +0.20366973720609016j ,
        0.09450462361437995  -0.10579300291497379j ,
        0.5843578754656225   +0.7250883727845516j  ,
       -0.8795803056850817   +0.971720533162076j   ,
        0.4667687591685125   +0.8978517228622711j  ,
        0.04797702782997082  -0.5476726466574942j  ,
       -0.2665074162740675   +0.0752324029980533j  ,
        0.7068066436868098   +0.650960715856507j   ,
       -0.7429125098381866   +0.24191988501507516j ,
       -0.941663626641849    +0.0440211602325864j  ,
        0.4527711246097275   +0.7802147434407857j  ,
        1.2670951866750226   +0.3826819182786586j  ,
       -0.04084747240977166  -0.15934453115125916j ,
       -0.31068342668697924  -0.021919010879470957j,
        0.3793153986909309   +0.7286305796586262j  ,
       -0.09135633626935058  +0.2521520500788982j  ,
        0.38283036127394887  -1.0493637043353699j  ,
        0.5322562208678986   -0.9111097091371199j  ,
       -0.033294863745490844 -0.1108967923622809j  ,
        0.13886509258616503  +1.129373998665531j   ,
        0.22361860129475364  +0.4133611523184811j  ,
        0.06951263978130012  +0.13609694096976044j ,
       -0.13632414329378406  -0.8992125989692281j  ,
       -0.9082516535087548   -0.3638029850828808j  ,
       -0.9584519354416745   +0.16299188920087965j ,
       -0.6315929144686548   +0.14895940574606037j ,
       -0.18897523484134549  -0.1380777946700359j  ,
        0.3285101718305785   +0.8355533156763867j  ,
        0.025584559886926095 +0.2551663188672287j  ,
        0.276747636015355    -0.9185318795454923j  ,
       -0.8586487391863051   -0.5999524372215721j  ,
       -0.8432705205216467   +0.07883221989846587j ,
       -0.670120673850388    +0.1664458754050091j  ,
       -0.2153889438747541   -0.3341896866248936j  ,
        1.1927974566730042   +0.5323478621394402j  ,
       -0.014937271528199604 +0.7108124053339271j  ,
       -0.2854205967030613   +0.5170402014875659j  ,
        0.5202050645229509   -1.0173267485025104j  ,
        0.553480843182039    +0.01581386426130595j ,
        0.7541310352188072   +0.22838458560698582j ,
       -0.06958673486291303  -0.8615889027310051j  ,
       -0.9718831879416943   -0.7162300775430247j  ,
        0.004568380942336109 +0.048292195108247504j,
        0.4913536046586128   -0.10429272272566664j ,
       -1.1172784751887526   -0.15026192887765816j ,
        0.060494033128144775 +1.0224593102416586j  ,
        1.0421186402335338   -0.1495402234413237j  ,
       -0.34175882598337914  -0.9976375763089045j  ,
       -0.4418783892916689   +0.09606248542670624j ,
        0.8502915482556148   +0.6278795516831366j  ,
        1.0393000586524352   -0.17934661968016588j ,
       -0.4428318071623186   -0.08185379169154638j ,
       -0.03840219211871326  +0.3806733800901507j  ,
        0.7740820608781789   -0.924384433059227j   ,
       -0.06167217403691509  -0.9314402414595253j  ,
       -0.11400934942587365  -0.48497235537363326j ,
       -0.0028636887583518567-1.1221186543315091j  ,
       -0.07270280692867603  +0.07124285584203287j ,
        0.28073051483508893  +0.5857275682614242j  ,
       -0.654984543856036    +0.8354231785661262j  ,
       -0.5187261917509268   +0.6019799926334745j  ,
       -0.4473579551406935   +0.17295971347710265j ,
       -0.9284783656351782   -0.8335198899206268j  ,
       -0.31778182883427525  -0.6188191745546093j  ,
        0.80962405464884     -0.8877716829190442j  ,
       -0.28078718449479595  -0.17295680174386513j ,
       -0.011206013797797343 +1.0808443743319494j  ,
        0.12407651502056877  +0.5625172473669444j  ,
       -0.6142909156079297   +0.7773840695944384j  ])

    out_frame = np.empty(frame_size, dtype=complex)
    frame_sync(in_frame, out_frame)
    assert np.allclose(out_frame, expected_frame)
