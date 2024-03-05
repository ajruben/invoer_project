#osgeo (GDAL/ogr) installeren: pip install (file die in gdal_wheel staat), ga anders naar https://github.com/cgohlke/geospatial-wheels/releases of https://github.com/cgohlke/geospatial-wheels
#can also use something like fiona, is easier/less writing.
#note: creating large geopackages takes a long time, reading them doesnt.
#TODO inv -> gpkg?
#TODO rnadom values verbeteren voor bouwwerk ->  kies waarde tussen 0,100 in tientallen. filter gelijke bandbreedtes.
from osgeo import ogr
import random
import math
from itertools import chain

geometries_dict = {}
#beschrijvingen bij parameters toevoegen TODO
band = [random.randrange(11)/10 for i in range(1,11)]
#bouwwerk help variabelen
def make_reflection_bandbreedte(rows):
    band = [random.choice([int(i*10) for i in range(7,9)]) for i in range(int(rows))] 
    return band

rows = 2
feature_count_wegvakken = 2
nr_waarneempuntenxy = 5

#variabelen voor genereren waarneempunten
IDpunt = [str(i) for i in range(1,nr_waarneempuntenxy + 1)]
nr_waarneemhoogtes_per_punt = [random.randint(1,3) for i in range(nr_waarneempuntenxy)]
idhoogtes = [[IDpunt[i]] * nr_waarneemhoogtes_per_punt[i]  for i in range(len(IDpunt))]
idhoogtes = list(chain(*idhoogtes))
z_waarden = [i*2  for nr in nr_waarneemhoogtes_per_punt for i in range(1,nr+1)]

wegdektypes = ['referentiewegdek',
               '1L ZOAB',
               'akoestisch geoptimaliseerd 1L ZOAB',
               '2L ZOAB',
               '2L ZOAB fijn',
               'SMA 0/5',
               'SMA 0/8',
               'akoestisch geoptimaliseerd SMA',
               'uitgeborsteld beton',
               'geoptimaliseerd uitgeborsteld beton',
               'fijngebezemd beton',
               'oppervlakbewerking',
               'elementenverharding keperverband',
               'elementenverharding niet in keperverband',
               'stille elementenverharding',
               'dunne deklagen A',
               'dunne deklagen B',
               ]

table_schemas = {
    'bouwwerk':
    {   
        'table_name':'bouwwerk',
        'srs_id':28992,
        'geometry_type': ogr.wkbPolygonZM,
        'columns':[
             
                {'name': 'band63Hz', 'type': ogr.OFTReal},
                {'name': 'band125Hz', 'type': ogr.OFTReal},
                {'name': 'band250Hz', 'type': ogr.OFTReal},
                {'name': 'band500Hz', 'type': ogr.OFTReal},
                {'name': 'band1000Hz', 'type': ogr.OFTReal},
                {'name': 'band2000Hz', 'type': ogr.OFTReal},
                {'name': 'band4000Hz', 'type': ogr.OFTReal},
                {'name': 'band8000Hz', 'type': ogr.OFTReal}
        ],
        'feature_count': 10e6,
        'data': { 
             
                'band63Hz': make_reflection_bandbreedte(rows),
                'band125Hz': make_reflection_bandbreedte(rows),
                'band250Hz': make_reflection_bandbreedte(rows),
                'band500Hz': make_reflection_bandbreedte(rows),
                'band1000Hz': make_reflection_bandbreedte(rows),
                'band2000Hz': make_reflection_bandbreedte(rows),
                'band4000Hz': make_reflection_bandbreedte(rows),
                'band8000Hz': make_reflection_bandbreedte(rows)
                },
        'min_x':-1000,
        'max_x':1000,
        'min_y':-1000,
        'max_y':1000,
        'min_z':-10,
        'max_z':10,
        'min_m':-10,
        'max_m':10,
        'geometry_pattern' : 'random'
    },

    'bodemvlak':
    {
        'table_name':'bodemvlak',
        'srs_id':28992,
        'geometry_type':ogr.wkbPolygon,
        'columns':[
                {'name': 'absorptiefractie', 'type': ogr.OFTInteger} 
        ],
        'feature_count': 2,
        'data': {
                'absorptiefractie': [0, 0]
                },
        'min_x':-1000,
        'max_x':1000,
        'min_y':-1000,
        'max_y':1000,
        'geometry_pattern' : 'random'   
    },
    'hoogtelijn':
    {
        'table_name':'hoogtelijn',
        'srs_id':28992,
        'geometry_type': ogr.wkbLineString,
        'columns':[
                {'name': 'hoogtelijntype', 'type': ogr.OFTString} 
        ],
        'data' : {
            'hoogtelijntype':["hoogtelijn", "stomp scherm + hoogtelijn"]
        },
        'min_x':-1000,
        'max_x':1000,
        'min_y':-1000,
        'max_y':1000,
        'geometry_pattern' : 'random'   
    },
    
    #ONS DATAMODEL?: 
    'wegdeelGPP' : #In rekenhart: Wegvakken
    {
        'table_name':'wegdeelGPP',
        'srs_id':28992,
        'geometry_type':ogr.wkbLineStringZM,
        'columns':[
                {'name' : 'kenmerk', 'type': ogr.OFTString}, #optioneel, gericht op voeden rekenhart, dus voor invoer bestand.
                {'name' : 'wegdektype', 'type': ogr.OFTString}, #HEEFT 17 mogelijkheden, bij rekenhart is er de optie om 90-99, dit zijn spectra (ZIE WEGDEKCORRECTIES)
                {'name' : 'hellingcorrectie' ,'type': ogr.OFTInteger}, #0=nee, 1=ja, veld geeft aan of de hellingcorrectie uit de lijnkenmerken (X, Y, Z en type voertuig) moet worden berekend of niet #TODO is bool
                {'name' : 'groepnummer', 'type': ogr.OFTInteger},
                {'name' : 'plafondcorrectie','type': ogr.OFTReal},

                {'name' : 'emmissieDag64Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieDag125Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieDag250Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieDag500Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieDag1000Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieDag2000Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieDag4000Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieDag8000Hz', 'type' : ogr.OFTReal},

                {'name' : 'emmissieAvond64Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieAvond125Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieAvond250Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieAvond500Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieAvond1000Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieAvond2000Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieAvond4000Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieAvond8000Hz', 'type' : ogr.OFTReal},

                {'name' : 'emmissieNacht64Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieNacht125Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieNacht250Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieNacht500Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieNacht1000Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieNacht2000Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieNacht4000Hz', 'type' : ogr.OFTReal},
                {'name' : 'emmissieNacht8000Hz', 'type' : ogr.OFTReal},
                
                {'name' : 'aantalVerkeersgegevensWegDagLicht', 'type' : ogr.OFTReal},
                {'name' : 'aantalVerkeersgegevensWegDagMiddelzwaar', 'type' : ogr.OFTReal},
                {'name' : 'aantalVerkeersgegevensWegDagZwaar', 'type' : ogr.OFTReal},
                {'name' : 'aantalVerkeersgegevensWegDagMotoren', 'type' : ogr.OFTReal},

                {'name' : 'aantalVerkeersgegevensWegAvondLicht', 'type' : ogr.OFTReal}, 
                {'name' : 'aantalVerkeersgegevensWegAvondMiddelzwaar', 'type' : ogr.OFTReal},
                {'name' : 'aantalVerkeersgegevensWegAvondZwaar', 'type' : ogr.OFTReal},
                {'name' : 'aantalVerkeersgegevensWegAvondMotoren', 'type' : ogr.OFTReal},

                {'name' : 'aantalVerkeersgegevensWegNachtLicht', 'type' : ogr.OFTReal},
                {'name' : 'aantalVerkeersgegevensWegNachtMiddelzwaar', 'type' : ogr.OFTReal},
                {'name' : 'aantalVerkeersgegevensWegNachtZwaar', 'type' : ogr.OFTReal},
                {'name' : 'aantalVerkeersgegevensWegNachtMotoren', 'type' : ogr.OFTReal},

                {'name' : 'snelheidVerkeersgegevensWegDagLicht', 'type' : ogr.OFTInteger},
                {'name' : 'snelheidVerkeersgegevensWegDagMiddelzwaar', 'type' : ogr.OFTInteger},
                {'name' : 'snelheidVerkeersgegevensWegDagZwaar', 'type' : ogr.OFTInteger},
                {'name' : 'snelheidVerkeersgegevensWegDagMotoren', 'type' : ogr.OFTInteger},

                {'name' : 'snelheidVerkeersgegevensWegAvondLicht', 'type' : ogr.OFTInteger},
                {'name' : 'snelheidVerkeersgegevensWegAvondMiddelzwaar', 'type' : ogr.OFTInteger},
                {'name' : 'snelheidVerkeersgegevensWegAvondZwaar', 'type' : ogr.OFTInteger},
                {'name' : 'snelheidVerkeersgegevensWegAvondMotoren', 'type' : ogr.OFTInteger},

                {'name' : 'snelheidVerkeersgegevensWegNachtLicht', 'type' : ogr.OFTInteger},
                {'name' : 'snelheidVerkeersgegevensWegNachtMiddelzwaar', 'type' : ogr.OFTInteger},
                {'name' : 'snelheidVerkeersgegevensWegNachtZwaar', 'type' : ogr.OFTInteger},
                {'name' : 'snelheidVerkeersgegevensWegNachtMotoren', 'type' : ogr.OFTInteger},  
        ],
        'feature_count': feature_count_wegvakken,
        'data': {
                'kenmerk': [""] * feature_count_wegvakken, #optioneel mag vanalles zijn
                'wegdektype': [random.choice(wegdektypes) for i in range(1 , 1 + feature_count_wegvakken)],
                'hellingcorrectie': [random.choice([0,1]) for i in range(1, feature_count_wegvakken + 1)], #ja nee
              
                'groepnummer' : [1 for i in range(1, feature_count_wegvakken + 1)],
                'plafondcorrectie': [random.uniform(-9.9, 9.9) for i in range(1, feature_count_wegvakken + 1)],

                'emmissieDag64Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieDag125Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieDag250Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieDag500Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieDag1000Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieDag2000Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieDag4000Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieDag8000Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],

                'emmissieAvond64Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieAvond125Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieAvond250Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieAvond500Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieAvond1000Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieAvond2000Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieAvond4000Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieAvond8000Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],

                'emmissieNacht64Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieNacht125Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieNacht250Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieNacht500Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieNacht1000Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieNacht2000Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieNacht4000Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],
                'emmissieNacht8000Hz': [random.uniform(0, 200) for i in range(1,feature_count_wegvakken + 1)],


                'aantalVerkeersgegevensWegDagLicht' : [random.uniform(0, 100000) for i in range(1,feature_count_wegvakken + 1)],
                'aantalVerkeersgegevensWegDagMiddelzwaar' : [random.uniform(0, 100000) for i in range(1,feature_count_wegvakken + 1)],
                'aantalVerkeersgegevensWegDagZwaar' : [random.uniform(0, 100000) for i in range(1,feature_count_wegvakken + 1)],
                'aantalVerkeersgegevensWegDagMotoren' : [random.uniform(0, 100000) for i in range(1,feature_count_wegvakken + 1)],
                
                'aantalVerkeersgegevensWegAvondLicht' : [random.uniform(0, 100000) for i in range(1,feature_count_wegvakken + 1)],
                'aantalVerkeersgegevensWegAvondMiddelzwaar' : [random.uniform(0, 100000) for i in range(1,feature_count_wegvakken + 1)],
                'aantalVerkeersgegevensWegAvondZwaar' : [random.uniform(0, 100000) for i in range(1,feature_count_wegvakken + 1)],
                'aantalVerkeersgegevensWegAvondMotoren' : [random.uniform(0, 100000) for i in range(1,feature_count_wegvakken + 1)],
                
                'aantalVerkeersgegevensWegNachtLicht' : [random.uniform(0, 100000) for i in range(1,feature_count_wegvakken + 1)],
                'aantalVerkeersgegevensWegNachtMiddelzwaar' : [random.uniform(0, 100000) for i in range(1,feature_count_wegvakken + 1)],
                'aantalVerkeersgegevensWegNachtZwaar' : [random.uniform(0, 100000) for i in range(1,feature_count_wegvakken + 1)], #50 80 100
                'aantalVerkeersgegevensWegNachtMotoren' : [random.uniform(0, 100000) for i in range(1,feature_count_wegvakken + 1)], #50 80 100


                'snelheidVerkeersgegevensWegDagLicht' : [random.choice([50, 80, 100]) for i in range (1,feature_count_wegvakken + 1)],
                'snelheidVerkeersgegevensWegDagMiddelzwaar' : [random.choice([50, 80, 100]) for i in range (1,feature_count_wegvakken + 1)],
                'snelheidVerkeersgegevensWegDagZwaar' : [random.choice([50, 80, 100]) for i in range (1,feature_count_wegvakken + 1)],
                'snelheidVerkeersgegevensWegDagMotoren' : [random.choice([50, 80, 100]) for i in range (1,feature_count_wegvakken + 1)],


                'snelheidVerkeersgegevensWegAvondLicht' : [random.choice([50, 80, 100]) for i in range (1,feature_count_wegvakken + 1)],
                'snelheidVerkeersgegevensWegAvondMiddelzwaar' : [random.choice([50, 80, 100]) for i in range (1,feature_count_wegvakken + 1)],
                'snelheidVerkeersgegevensWegAvondZwaar' : [random.choice([50, 80, 100]) for i in range (1,feature_count_wegvakken + 1)],
                'snelheidVerkeersgegevensWegAvondMotoren' : [random.choice([50, 80, 100]) for i in range (1,feature_count_wegvakken + 1)],


                'snelheidVerkeersgegevensWegNachtLicht' : [random.choice([50, 80, 100]) for i in range (1,feature_count_wegvakken + 1)],
                'snelheidVerkeersgegevensWegNachtMiddelzwaar' : [random.choice([50, 80, 100]) for i in range (1,feature_count_wegvakken + 1)],
                'snelheidVerkeersgegevensWegNachtZwaar' : [random.choice([50, 80, 100]) for i in range (1,feature_count_wegvakken + 1)],
                'snelheidVerkeersgegevensWegNachtMotoren' : [random.choice([50, 80, 100]) for i in range (1,feature_count_wegvakken + 1)]

                },
        'min_x':-1000,
        'max_x':1000,
        'min_y':-1000,
        'max_y':1000,
        'min_z':-100,
        'max_z':100,
        'min_m':-100,
        'max_m':100,
        'geometry_pattern' : 'random'
    },
    'geluidschermdeel' :
    {
        'table_name':'geluidschermdeel',
        'srs_id':28992,
        'geometry_type':ogr.wkbLineString,
        'columns':[
                {'name' : 'profieltype', 'type': ogr.OFTString}, #type in rh
                {'name' : 'hellingshoek', 'type': ogr.OFTInteger}, #graden tov verticaal
                ##overhoogtes gaan weg,1 hoogte, zwaarde gebruiken als hoogte, veldhoogte1 opgeteld.
                {'name' : 'reflectiefactorRechts|FactorPerOctaafband|band31Hz', 'type':  ogr.OFTReal}, #tussen 0 en 1
                {'name' : 'reflectiefactorRechts|FactorPerOctaafband|band63Hz', 'type': ogr.OFTReal}, 
                {'name' : 'reflectiefactorRechts|FactorPerOctaafband|band125Hz', 'type': ogr.OFTReal}, 
                {'name' : 'reflectiefactorRechts|FactorPerOctaafband|band250z', 'type': ogr.OFTReal}, 
                {'name' : 'reflectiefactorRechts|FactorPerOctaafband|band500Hz', 'type': ogr.OFTReal}, 
                {'name' : 'reflectiefactorRechts|FactorPerOctaafband|band1000Hz', 'type': ogr.OFTReal}, 
                {'name' : 'reflectiefactorRechts|FactorPerOctaafband|band2000Hz', 'type': ogr.OFTReal}, 
                {'name' : 'reflectiefactorRechts|FactorPerOctaafband|band4000Hz', 'type': ogr.OFTReal}, 
                {'name' : 'reflectiefactorRechts|FactorPerOctaafband|band8000Hz', 'type': ogr.OFTReal}, 
                {'name' : 'statusZwevend', 'type': ogr.OFTInteger}, #bool

                {'name' : 'band31Hz', 'type': ogr.OFTReal}, #Adiff 
                {'name' : 'band63Hz', 'type': ogr.OFTReal}, 
                {'name' : 'band125Hz', 'type': ogr.OFTReal}, 
                {'name' : 'band250Hz', 'type': ogr.OFTReal}, 
                {'name' : 'band500Hz', 'type': ogr.OFTReal}, 
                {'name' : 'band1000Hz', 'type': ogr.OFTReal}, 
                {'name' : 'band2000Hz', 'type': ogr.OFTReal}, 
                {'name' : 'band4000Hz', 'type': ogr.OFTReal}, 
                {'name' : 'band8000Hz', 'type': ogr.OFTReal}, 
        ],
        'feature_count': 10,
        'data': {
                'profieltype' : [random.choice(["scherp", "stomp"]) for i in range(1,11)], #type in rh
                'hellingshoek' : [random.uniform(0, 5) for i in range(1,11)], #graden tov verticaal
                'reflectiefactorRechts|FactorPerOctaafband|band31Hz' : band,
                'reflectiefactorRechts|FactorPerOctaafband|band63Hz' : band, 
                'reflectiefactorRechts|FactorPerOctaafband|band125Hz' : band, 
                'reflectiefactorRechts|FactorPerOctaafband|band250z' : band, 
                'reflectiefactorRechts|FactorPerOctaafband|band500Hz' : band, 
                'reflectiefactorRechts|FactorPerOctaafband|band1000Hz' : band, 
                'reflectiefactorRechts|FactorPerOctaafband|band2000Hz' : band, 
                'reflectiefactorRechts|FactorPerOctaafband|band4000Hz' : band, 
                'reflectiefactorRechts|FactorPerOctaafband|band8000Hz' : band, 
                'statusZwevend': [0] * 10,

                'band31Hz': band,
                'band63Hz': band,
                'band125Hz': band,
                'band250Hz': band,
                'band500Hz': band,
                'band1000Hz': band,
                'band2000Hz': band,
                'band4000Hz': band,
                'band8000Hz': band
                },
        'min_x':-1000,
        'max_x':1000,
        'min_y':-1000,
        'max_y':1000,
        'geometry_pattern' : 'random'
    },
    
    'Waarneempunt':
    {
        'table_name':'Waarneempunt',
        'srs_id':28992,
        'geometry_type': ogr.wkbPointZM,
        'columns':[
                {'name': 'ID', 'type': ogr.OFTString},
                {'name': 'X', 'type': ogr.OFTReal},
                {'name': 'Y', 'type': ogr.OFTReal},
                {'name': 'M', 'type': ogr.OFTReal},
                {'name': 'maaiveldBerekenen', 'type' : ogr.OFTInteger},
                {'name':'type', 'type': ogr.OFTString},
                {'name':'reflectiesAantal', 'type': ogr.OFTString},
                {'name': 'ID_Pand', 'type': ogr.OFTInteger},
                {'name': 'opermerking1', 'type': ogr.OFTString},
                {'name': 'opermerking2', 'type': ogr.OFTString}
        ],
        'data' : {
            'ID':IDpunt,
            'X':[i*100 for i in range(1,nr_waarneempuntenxy + 1)],
            'Y':[i*100 for i in range(1,nr_waarneempuntenxy + 1)],
            'M':[0] * nr_waarneempuntenxy,
            'type': ['V'] * nr_waarneempuntenxy,
            'maaiveldBerekenen' : [0] * nr_waarneempuntenxy,
            'reflectiesAantal': ['S'] * nr_waarneempuntenxy,
            'ID_Pand':[""] * nr_waarneempuntenxy,
            'opermerking1':[""] * nr_waarneempuntenxy,
            'opermerking2':[""] * nr_waarneempuntenxy
        },
        'min_x':-1000,
        'max_x':1000,
        'min_y':-1000,
        'max_y':1000,
        'geometry_pattern' : 'none'  
    },
    'WaarneempuntHoogte':
    {
        'table_name':'WaarneempuntHoogte',
        'srs_id':28992,
        'geometry_type': ogr.wkbNone,
        'columns':[
                {'name': 'ID', 'type': ogr.OFTString},
                {'name': 'Z', 'type': ogr.OFTReal},
                {'name': 'Lcorrectie', 'type': ogr.OFTReal}
        ],
        'data' : {
            'ID':idhoogtes,
            'Z':z_waarden,
            'Lcorrectie':[0] * len(z_waarden)
        },
    },
}


class Geopackage(): #TODO, replace print statements. is fine for now
    """"
    This class allows the creation of new geopackages based on an empty gpkg template.
    Methods were created with the idea of simplifying working with geopackages via python (and SQLite3).
    methods are speficially created to deal with X
    """
    def __init__(self, geopackage, empty_geopackage="data\\empty.gpkg", create=True):
        #create new empty geopackage inside output folder.
        import shutil
        if create == True:
            self.geopackage_name = geopackage
            geopackage = "output\\" + geopackage
            #track if geopackage is created
            self.geopackage_location = geopackage
            shutil.copy(empty_geopackage, geopackage)
        #Track connection status, at first closed. (so cant close an unopened gpkg)
        else:
            self.geopackage_name = geopackage
            self.geopackage_location = geopackage

        self.con = None
        self.cur = None
        self.srs_id = 28992 #for add_X functions, ?relevant for dutch related geodata? (amersfoort srs)
    
    #----------------------------------------------------------------------------------------------------
    #methods do deal with the geopackage, such as connecting, closing, removing and displaying information. basically sqlite query shortcuts
    def connect(self):
        """
        Method to open connection to gpkg
        """
        import sqlite3
        self.con = sqlite3.connect(self.geopackage_location)
        self.cur = self.con.cursor()
        print(f"""---------------------------------------------------------------------------------------------------------------------------\n------------------------------------------- !Connection to {self.geopackage_name} is opened! -------------------------------------------\n---------------------------------------------------------------------------------------------------------------------------""")

    def close(self):
        """
        Method to close connection to gpkg
        """
        if self.con != None:
            self.cur.close()
            self.con.close()
            print(f"""---------------------------------------------------------------------------------------------------------------------------\n------------------------------------------- !Connection to {self.geopackage_name} is closed! -------------------------------------------\n---------------------------------------------------------------------------------------------------------------------------""")
            #to track whether connection is closed
            self.con = None
            self.cur = None
            self.geopackage_path = None
        else:
            print("!Connection already closed.")
        
    def rem(self):
        """
        method to remove created gpkg, both if connection is of/online
        first close connection if online.
        """
        import os
        if self.con != None:
            self.cur.close()
            self.con.close()
            print(f"""---------------------------------------------------------------------------------------------------------------------------\n------------------------------------------- !Connection to {self.geopackage_name} is closed! -------------------------------------------\n---------------------------------------------------------------------------------------------------------------------------""")
            #to track whether connection is closed
            self.con = None
            self.cur = None
            os.remove(self.geopackage_location)
            print(f"!Geopackage {self.geopackage_name} is removed.")
            self.geopackage_path = None
        else:
            os.remove(self.geopackage_location)
            
    def tables(self):
        """
        Method to display all tables in the gpkg
        """
        table_qry = "SELECT name FROM sqlite_master WHERE type=?;"
        self.cur.execute(table_qry, ('table',))
        result = self.cur.fetchall()
        print("All tables:\n", result)

    def column_info(self, table, display=True):
        """
        Method to display column info of a table in the gpkg
        """
        table_qry2 = f"PRAGMA table_info({table})"
        self.cur.execute(table_qry2)
        result = self.cur.fetchall()
        if display:
            print(f"\nInfo {table}:\n", result)
        return result

    def column_names(self, table, display = False):
        columns = self.column_info(f'{table}', display)
        column_names = [column[1] for column in columns if column[1] not in ('fid', 'geom')] #not selecting fid and geom.
        return column_names

    def select_by_column_order(self, table, order):
        sql_query = f"SELECT {', '.join(order)} FROM {table}"
        self.cur.execute(sql_query)
        result = self.cur.fetchall()
        return result

    def content(self, table, display=True):
        """
        Method to display the content of a table, row for row (tuples)
        """
        select_qry = f"""
        SELECT * from {table}
        """
        self.cur.execute(select_qry)
        rows = self.cur.fetchall()
        if display:
            print(f"\nContent of {table}:")
            for row in rows:
                print(row)
        return rows
    
    def retrieve_coordinates(self, table):
        """
        method to blabla
        """
        select_qry = f"SELECT * FROM {table} ORDER BY id"
        self.cur.execute(select_qry)
        data = self.cur.fetchall()
        return data

        
    #----------------------------------------------------------------------------------------------------
    #methods do deal with adding information to geopackage, such as adding the srs or adding a feature table
    def add_Amersfoort_srs(self): 
        """
        Method to add the srs often used at dBvision/The Netherlands.
        """
        #variables
        srs_name = 'Amersfoort / RD New'
        srs_id = self.srs_id
        organization = 'EPSG'
        organization_coordsys_id = 28992
        definition = 'PROJCS["Amersfoort / RD New",GEOGCS["Amersfoort",DATUM["Amersfoort",SPHEROID["Bessel 1841",6377397.155,299.1528128,AUTHORITY["EPSG","7004"]],AUTHORITY["EPSG","6289"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4289"]],PROJECTION["Oblique_Stereographic"],PARAMETER["latitude_of_origin",52.1561605555556],PARAMETER["central_meridian",5.38763888888889],PARAMETER["scale_factor",0.9999079],PARAMETER["false_easting",155000],PARAMETER["false_northing",463000],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","28992"]]'
        description = None
        # Check if srs_id already exists
        self.cur.execute("SELECT COUNT(*) FROM gpkg_spatial_ref_sys WHERE srs_id = ?", (srs_id,))
        count = (self.cur.fetchall())[0][0]
        if count > 0:
            print("INFO: Amersfoort srs ALREADY PRESENT")
        else:
            srs_qry = """
                INSERT INTO gpkg_spatial_ref_sys (srs_name, srs_id, organization, organization_coordsys_id, definition, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            self.cur.execute(srs_qry, (srs_name, srs_id, organization, organization_coordsys_id, definition, description))
            self.con.commit()
            print(f"INFO: Amersfoort srs inserted into gpkg_spatial_ref_sys successfully.")
    
    #----------------------------------------------------------------------------------------------------------------
    def add_feature_table(self, new_table_name, table_schema):
        """
        Adding feature table using ogr.

        #-----------------------------------------------------
        method layout (top to bottom):
        0. Open geopackage, set up variables needed for the creation of a layer/feature table in a geopackage, check geometry_type
        1. b)launch appropriate layer creater according to a) geometry_type
        2. Create the layer, give it columns (name+type) and add data (features).
        3. launch appopriate geometry creater (by inserting WKT, asumption: ogr translates this to GeoPackageBinary and use rtree #TODO check actual process), insert given data+geometry as features into the feature table
        4. Creating WKT lists, thus containing geometry information in WKT format.

        #-----------------------------------------------------
        input:
        string new_table_name, dictionary table_schema['table_name'] (which I passed as table_schema)
        
        table_schema['table_name'] has format along with default values:
        {
        'table_name':'name',
        'srs_id':28992,
        'geometry_type':ogr.wkbNone,
        'columns':[
            {'name': str(X), 'type': str(Y)]}
        ],
        'feature_count': 1,
        'data': {
                'str(X)': list(data(type=Y))
                },
        'min_x':-1000,
        'max_x':1000,
        'min_y':-1000,
        'max_y':1000,
        'geometry_pattern' : 'random'
        }

        output:
        feature table added to geopackage, along with rtree tables and relevant rows inside 'standard' geopakcage tables, such as 'gpkg_contents' etc.

        #--------------------------------------------------
        ogr background:
        https://gdal.org/api/python/osgeo.ogr.html
        https://pcjericks.github.io/py-gdalogr-cookbook/

        installing ogr/osgeo: 
        pip install "file location of gdal_wheel", to be downloaded from https://github.com/cgohlke/geospatial-wheels/releases, check out https://github.com/cgohlke/geospatial-wheels
        """
        #0. Open geopackage using ogr
        from osgeo import ogr 

        driver = ogr.GetDriverByName("GPKG")
        geopackage = driver.Open(self.geopackage_location, 1)  #rw
        #set up variables
        spatial_reference = ogr.osr.SpatialReference(); spatial_reference.ImportFromEPSG(table_schema['srs_id'])
        layer_name = new_table_name
        geometry = table_schema['geometry_type']
        
        #1a. check geometry_type
        if geometry:
            self.__geometry_checker(geometry, geopackage, layer_name, spatial_reference, table_schema)
        geopackage = None

    #helper functions for creating feature tables (generally gpkg calls it feature tables, qgis calls it layers)
    #-------------------------------------------------------------------------------------------------------------------
    #1b. launch appropriate layer creater: determine geometry
    def __geometry_checker(self, geometry, geopackage,layer_name, spatial_reference, table_schema):
        if geometry == ogr.wkbPolygon or geometry == ogr.wkbPolygonZM or geometry == 3003:
            self.__Create_Polygon(geopackage,layer_name, spatial_reference, table_schema) #double geom, check later #TODOs
        elif geometry == ogr.wkbLineString or geometry == ogr.wkbLineStringZM or geometry == 3002:
            self.__Create_Line(geopackage,layer_name, spatial_reference, table_schema)
        elif geometry == ogr.wkbPointZM:
            self.__Create_Point(geopackage,layer_name, spatial_reference, table_schema)
        elif geometry == ogr.wkbNone:
            self.__Create_Attribute(geopackage,layer_name, spatial_reference, table_schema)
    
    #2. Create the layer, give it columns (name+type) and add data (features). #TODO: ifelse statements instead?
    def __Create_Point(self, geopackage, layer_name, spatial_reference, table_schema):
        layer = geopackage.CreateLayer(layer_name, spatial_reference, ogr.wkbPoint)
        # Add attribute fields to the layer (customize based on your data)
        self.__Create_Columns(layer=layer, table_schema=table_schema)
        self.__Create_Features_from_data_Point(layer=layer, table_schema=table_schema)

    def __Create_Polygon(self, geopackage, layer_name, spatial_reference, table_schema):
        layer = geopackage.CreateLayer(layer_name, spatial_reference, ogr.wkbPolygonZM)
        # Add attribute fields to the layer (customize based on your data)
        self.__Create_Columns(layer=layer, table_schema=table_schema)
        self.__Create_Features_from_data_Polygon(layer=layer, table_schema=table_schema)

    def __Create_Line(self, geopackage, layer_name, spatial_reference, table_schema):
        layer = geopackage.CreateLayer(layer_name, spatial_reference, ogr.wkbLineStringZM)
        # Add attribute fields to the layer (customize based on your data)
        self.__Create_Columns(layer=layer, table_schema=table_schema)
        self.__Create_Features_from_data_Line(layer=layer, table_schema=table_schema)

    def __Create_Attribute(self, geopackage, layer_name, spatial_reference, table_schema):
        layer = geopackage.CreateLayer(layer_name, spatial_reference, ogr.wkbNone)
        # Add attribute fields to the layer (customize based on your data)
        self.__Create_Columns(layer=layer, table_schema=table_schema)
        self.__Create_Features_from_data_Attribute(layer=layer, table_schema=table_schema)

    #Intermezzo: helper functions for creating columns     
    def __Create_Columns(self, layer, table_schema):
        for column_info in table_schema['columns']:
            column_name = column_info['name']
            column_type = column_info['type']
            layer.CreateField(ogr.FieldDefn(column_name, column_type))

    #3. Adding given data as features into the feature table, for each geometry type (TODO: generalize, unnecessary to define method for each type, just happened to be developed this way)
    def __Create_Features_from_data_Attribute(self, layer, table_schema):
        data = table_schema['data']
        WKT = None
        self.__create_features(layer, data, WKT)
    
    def __Create_Features_from_data_Point(self, layer, table_schema):
        if table_schema['geometry_pattern'] == 'random':
            WKT = self.__Create_PointWKT_random(table_schema)
        if table_schema['geometry_pattern'] == 'none':
            WKT = self.__Create_PointWKT(table_schema)
        data = table_schema['data']
        self.__create_features(layer, data, WKT)

    def __Create_Features_from_data_Polygon(self, layer, table_schema):
        if table_schema['geometry_pattern'] == 'diagonal':
            WKT = self.__Create_PolygonsWKT_diagonal(table_schema)
        if table_schema['geometry_pattern'] == 'random_rect':
            WKT = self.__Create_rect_PolygonsWKT_random(table_schema)
        if table_schema['geometry_pattern'] == 'random':
            WKT = self.__Create_PolygonsWKT_semi_random(table_schema)
        if table_schema['geometry_pattern'] == 'RANDOM':
            WKT = self.__Create_PolygonsWKT_random(table_schema)
        data = table_schema['data']
        self.__create_features(layer, data, WKT)
    
    

    def __Create_Features_from_data_Line(self, layer, table_schema):
        if table_schema['geometry_pattern'] == 'random':
            WKT = self.__Create_Sep_LineStringsWKT_random(table_schema)
        data = table_schema['data']
        self.__create_features(layer, data, WKT)
        
    #helper helper function
    def __create_features(self, layer, data, WKT):
        for i in range(len(data[next(iter(data))])):

            feature = ogr.Feature(layer.GetLayerDefn())
            if WKT != None:
                feature.SetGeometry(ogr.CreateGeometryFromWkt(WKT[i]))
            for key in data:

                feature.SetField(key, data[key][i])
            # Add the feature to the layer
            layer.CreateFeature(feature)
            if i%1000 == 0:
                print(f"feature {i} added")

    #4. Creating WKT lists, thus containing geometry information in WKT format. This part actually makes the geo part of the feature table. (feature.SetGeometry(ogr.CreateGeometryFromWkt(polygonsWKT[i])))
    def __Create_PointWKT(self, table_schema):
        data = table_schema['data']
        points = []
        for i in range(len(data['X'])):
            x = data['X'][i]
            y = data['Y'][i]
            m = data['M'][i]
            point_wkt = f"POINT ({x} {y} 0.00 {m})"
            points.append(point_wkt)
        return points
    
    def __Create_PointWKT_random(self, table_schema):
        import random
        points = []
        max_x, max_y, min_x, min_y, data, num = self.__variables(table_schema)
        for i in range(num):
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            point_wkt = f"POINT ({x} {y})"
            points.append(point_wkt)
        return points

    def __Create_Sep_LineStringsWKT_random(self, table_schema):
        import random
        linestrings = []
        max_x, max_y, min_x, min_y, min_z, max_z, min_m, max_m, data, num = self.__variables(table_schema)
        for i in range(num):
            start_x = random.uniform(min_x, max_x)
            start_y = random.uniform(min_y, max_y)
            start_z = random.uniform(min_z, max_z)
            start_m = random.uniform(min_m, max_m)
            size_x = random.uniform(-(max_x - min_x) / num, (max_x - min_x) / num)
            size_y = random.uniform(-(max_x - min_x) / num, (max_y - min_y) / num)
            size_z = random.uniform(-0.5, 0.5)
            size_m = size_z
            end_x = start_x + size_x
            end_y = start_y + size_y
            end_z = start_z + size_z
            end_m = start_m + size_m
            linestring_str = f'LINESTRING ZM({start_x} {start_y} {start_z} {start_m}, {end_x} {end_y} {end_z} {end_m})'
            linestrings.append(linestring_str)
        return linestrings

    def __Create_Connected_LineStringsWKT_random(self, table_schema):
        import random
        linestrings = []
        max_x, max_y, min_x, min_y, min_z, max_z, min_m, max_m, data, num = self.__variables(table_schema)
        start_x = random.uniform(min_x, max_x)
        start_y = random.uniform(min_y, max_y)
        start_z = random.uniform(min_z, max_z)
        start_m = random.uniform(min_m, max_m)
        for i in range(num):
            size_x = random.uniform(-(max_x - min_x) / num, (max_x - min_x) / num)
            size_y = random.uniform(-(max_x - min_x) / num, (max_y - min_y) / num)
            size_z = random.uniform(-0.5, 0.5)
            size_m = size_z
            end_x = start_x + size_x
            end_y = start_y + size_y
            end_z = start_z + size_z
            end_m = start_m + size_m
            linestring_str = f'LINESTRING ZM({start_x} {start_y} {start_z} {start_m}, {end_x} {end_y} {end_z} {end_m})'
            linestrings.append(linestring_str)
            start_x, start_y, start_z, start_m = end_x, end_y, end_z, end_m
        return linestrings
    
    def __Create_PolygonsWKT_diagonal(self, table_schema):
        polygons = []
        max_x, max_y, min_x, min_y, data, num = self.__variables(table_schema)
        step_x = (max_x - min_y) / num
        step_y = (max_y - min_y) / num
        for i in range(num):
            start_x = min_x + i * step_x
            end_x = start_x + step_x
            start_y = min_y + i * step_y
            end_y = start_y + step_y
            polygon_str = f'POLYGON(({start_x} {start_y}, {start_x} {end_y}, {end_x} {end_y}, {end_x} {start_y}, {start_x} {start_y}))'
            polygons.append(polygon_str)
        return polygons
    
    def __Create_rect_PolygonsWKT_random(self, table_schema):
        import random
        polygons = []
        max_x, max_y, min_x, min_y, data, num = self.__variables(table_schema)
        for i in range(num):
            start_x = random.uniform(min_x, max_x)
            start_y = random.uniform(min_y, max_y)
            size_x = random.uniform(0, (max_x - min_x) / num)
            size_y = random.uniform(0, (max_y - min_y) / num)
            end_x = start_x + size_x
            end_y = start_y + size_y
            polygon_str = f'POLYGON(({start_x} {start_y}, {start_x} {end_y}, {end_x} {end_y}, {end_x} {start_y}, {start_x} {start_y}))'
            polygons.append(polygon_str)
        return polygons
    
    def __Create_PolygonsWKT_semi_random(self, table_schema):
        import random
     
        polygons = []
        max_x, max_y, min_x, min_y, min_z, max_z, min_m, max_m, data, num = self.__variables(table_schema)
        
        for i in range(num):
            coord_list = []
            #center polygon
            #random starting point
            center_x = random.uniform(min_x, max_x)
            center_y = random.uniform(min_y, max_y)
    
            corners_num = random.randint(3,8)
            max_side = max(max_x - min_x, max_y - min_y) #for r condition, take longest side. 
            # get r
            def random_r(minr = (1/50 * max_side) * (num)**(-1/2), maxr = (1/10 * max_side) * (num)**(-1/2)):
                r_factor = 15
                if r_factor < 2:
                    minr = minr - (minr * (r_factor -1))
                    maxr = maxr * r_factor
                else:
                    maxr = maxr * 3
                    minr = minr / r_factor
                r = random.uniform(minr, maxr)
                flag = False
                i = 0
                while flag is False and i<100:
                    if (r + center_x > max_x) or (r + center_y > max_y) or (r - center_x < min_x) or (r - center_y < min_y):
                        r = random.uniform(minr, r)
                    if i==99:
                        r = max_side/20
                    else:
                        flag = True
                return r
            r = random_r()
            #get theta in degrees
            def generate_random_angles(n): 
                total_sum = 360
                factor = 1.5
                max_angle = ((total_sum) / (n)) * factor
                if factor<2:
                    min_angle = (total_sum) / (n) - (((total_sum) / (n)) * (factor-1)) 
                else:
                    min_angle = ((total_sum) / (n)) / factor
                size = 361
                while  size>360:
                    random_values = sorted(random.uniform(min_angle, max_angle) for _ in range(n-1))
                    size = sum(random_values)
                    
                return random_values
            #random hoeken. moeten optellen tot 360, per punt een hoek, elk punt telt bij de ander op.
            angles = generate_random_angles(corners_num)
            #print(angles)
            theta = random.randint(0,359)
            x_start = center_x + r * math.cos(math.radians(theta))
            y_start = center_y + r * math.sin(math.radians(theta))
            z_coord = 0
            m_coord = 0
            for corner in range(0, len(angles)):
                #r = random_r()
                theta += angles[corner]
                x_coord = center_x + r * math.cos(math.radians(theta))
                y_coord = center_y + r * math.sin(math.radians(theta))
               
                z_coord += random.uniform(-1, 2)#/corners_num
                m_coord += (random.uniform(-1, 2))#/corners_num
               
                coord_list.append((x_coord,y_coord,z_coord,m_coord))

            polygon_start = f'POLYGON ZM(({x_start} {y_start} {0} {0}, ' 
            polygon_coords = [str(coords[0]) + ' ' + str(coords[1]) + ' ' +  str(coords[2]) + ' ' + str(coords[3]) + ', ' for coords in coord_list]
            coord_string = ''
            for k in range(len(polygon_coords)):
                coord_string += polygon_coords[k]
            polygon_end = f'{x_start} {y_start} {0} {0}))'
            polygon_string = polygon_start + coord_string + polygon_end
            polygons.append(polygon_string)
       
    
        return polygons

    def __Create_PolygonsWKT_random(self, table_schema):
        """
        Depending on your settings, it can take a long time.
        """
        #https://github.com/prochitecture/sweep_intersector, https://github.com/prochitecture/sweep_intersector.git
        #sweeper: credits to vvoovv and polarkernel
        from sweep.sweep_intersector.SweepIntersectorLib.SweepIntersector import SweepIntersector
        
        import random
        polygons = []
        max_x, max_y, min_x, min_y, data, num = self.__variables(table_schema)
        for i in range(num):
            coord_list = []
            #polygon drawing board--------------------------------------------------------
            #center of polygon drawing board:
            center_x = random.uniform(min_x, max_x)
            center_y = random.uniform(min_y, max_y)

            Rad = max((max_x-min_x), (max_y-min_y))/5 #radius of polygon drawing board
            
            #First vector r1----------------------------------------------------------------
            r = random.triangular(0,Rad, (1/3)*Rad)
            theta = random.randint(0,359)
            xr = r * math.cos(math.radians(theta))
            yr = r * math.sin(math.radians(theta))
            x1 = center_x + xr
            y1 = center_y + yr
           

            def generate_random_angles_radius(n):
                import random
                import math

                max_angle = 135
                min_angle = -135

                def generate_angles(n, start_index=0):
                    size = 0
                    angles = [random.triangular(min_angle, max_angle, 0) for _ in range(start_index, n)]
                    while not (340 <= size <= 360):
                        angles = [random.triangular(min_angle, max_angle, 0) for _ in range(start_index, n)]
                        size = sum(angles)
                    return angles

                rold = None
                last_valid_angles = None
                counter = 0
                coords = []
                x_coord = x1
                y_coord = y1
                

                while counter < (n-2):  # Allow retries without avoiding an infinite loop

                    print('counter', counter)
                    angles_new = generate_angles(n, counter)
                    r_new = [random.triangular(0, Rad/3, (abs((1/angle))/Rad)) for angle in angles_new]
                    if (last_valid_angles and rold) is not None:
                        angles = last_valid_angles + angles_new
                        r = r_old + r_new
                    else:
                        angles = angles_new
                        r = r_new
                   
                    
                    for radius, angle in zip(r, angles):
                        x_coord_old, y_coord_old = x_coord, y_coord
                        x_coord += radius * math.cos(math.radians(angle))
                        y_coord += radius * math.sin(math.radians(angle))
                        if (center_x - Rad < x_coord < center_x + Rad) and (center_y - Rad < y_coord < center_y + Rad):
                            coords.append((x_coord, y_coord))
                            counter += 1
                        else:
                            x_coord = x_coord_old
                            y_coord = y_coord_old
                            counter += 1
                            last_valid_angles = angles_new[:counter]
                            r_old = r[:counter]
                            break
                print(counter)           
                coords_list = coords
                
                coords = [((x1, y1), (coords[0]))] + [(coords[i], coords[i+1]) for i in range(len(coords)-1)] + [(coords[-1], (x1, y1))]#format as expected by sweeper
                return coords_list, coords
                
            def run():
                size = 1
                i=0
                while size > 0:
                    print(i, "run")
                    i+=1
                    n = 100
                    coord_list, coords = generate_random_angles_radius(n)

                    isector = SweepIntersector()
                    isecDic = isector.findIntersections(coords)
                    size = len(isecDic)
                    print(size)
                return coord_list
                
            coord_list = run()

            polygon_start = f'POLYGON(({x1} {y1}' 
            polygon_coords = [str(coords[0]) + ' ' + str(coords[1]) + ', ' for coords in coord_list]
            coord_string = ''
            for k in range(len(polygon_coords)):
               coord_string += polygon_coords[k]
            polygon_end = f'{x1} {y1}))'
            polygon_string = polygon_start + coord_string + polygon_end
            polygons.append(polygon_string)
        print(polygons)
        return polygons    


    def __variables(self, table_schema):
        max_x = table_schema['max_x']
        max_y = table_schema['max_y']
        min_x = table_schema['min_x']
        min_y = table_schema['min_y']
        min_z = table_schema['min_z']
        max_z = table_schema['max_z']
        min_m = table_schema['min_m']
        max_m = table_schema['max_m']
        data = table_schema['data']
        num = len(data[next(iter(data))])
        return max_x, max_y, min_x, min_y, min_z, max_z, min_m, max_m, data, num

if __name__ == '__main__':
    
    gpkg = Geopackage(geopackage="test.gpkg", create=True) 
   
    gpkg.connect()
    gpkg.add_feature_table('bouwwerk', table_schema = table_schemas['bouwwerk'])
    gpkg.add_feature_table('wegdeelGPP', table_schema = table_schemas['wegdeelGPP'])
    gpkg.add_feature_table('Waarneempunt', table_schema = table_schemas['Waarneempunt'])
    gpkg.add_feature_table('WaarneempuntHoogte', table_schema = table_schemas['WaarneempuntHoogte'])

    #gpkg.add_feature_table('geluidschermdeel', table_schema= table_schemas['geluidschermdeel'])
    #gpkg.add_feature_table('tblRekenpunt', table_schema= table_schemas['tblRekenpunt'])
    #gpkg.add_feature_table('tblRekenpunt_waarneemhoogte', table_schema= table_schemas['tblRekenpunt_waarneemhoogte'])
    #gpkg.column_info('bouwwerk')

    print(gpkg.column_names('bouwwerk'))
    #gpkg.tables()
    #gpkg.column_info('bouwwerk')
    
    gpkg.close()
    #gpkg.rem()





    