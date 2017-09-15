from imdb import IMDb
from pymarc import Record, Field
import csv
import datetime
import time
import string
import unidecode
import sys
from wcrecord import OCLCScraper
from marc_lang import lanugage_lookup

version = '1.6.2'
OCLCSymble = 'WIK'
today = datetime.date.today()
#create filename var
FILENAMEVAR = 'IMDB-' + str(time.time()) + '.mrc'

def invert_name(data):
    name_list = data['name'].split()
    name = name_list[-1] + ", "
    name_list = name_list[:-1]
    i = 0
    while i < len(name_list):
        name = name + name_list[i] +" "
        i += 1
    return unidecode.unidecode(name)

def find_mpaa(data):
    vMPAA = ''
    if 'certificates' in data:
        vMPAA = data['certificates']
        for MPAA in vMPAA:
            if 'USA:' in MPAA:
                vMPAA = str(MPAA)
                break
    return rating_fix(vMPAA)

def rating_fix(data):
    rating = str(data).upper()
    rating = rating[4:]
    rating = rating.split('::', 1)[0]
    return rating

def rating_text(data, worldcat):
    map_rate = {'text': 'MPAA rating: Not Rated', 'audiance' : ' '}
    
    rating = str(data).upper()
    if rating == 'G':
        map_rate['text'] = 'MPAA rating: G (General Audiences); Nothing that would offend parents for viewing by children.'
        map_rate['audiance'] = 'g'
    elif rating == 'PG':
        map_rate['text'] = 'MPAA rating: PG (Parental Guidance Suggested); Parents urged to give "parental guidance". May contain some material parents might not like for their young children.'
        map_rate['audiance'] = 'g'
    elif rating == 'PG-13':
        map_rate['text'] = 'MPAA rating: PG-13 (Parents Strongly Cautioned); Parents are urged to be cautious. Some material may be inappropriate for pre-teenagers.'
        map_rate['audiance'] = 'd'
    elif rating == 'R':
        map_rate['text'] = "MPAA rating: R (Restricted); Contains some adult material. Parents are urged to learn more about the film before taking their young children with them."
        map_rate['audiance'] = 'e'
    elif rating == 'NC-17':
        map_rate['text'] = "MPAA rating: NC-17 (Adults Only); Should not be viewed by anyone under 17"
        map_rate['audiance'] = 'e'

    if 'TV' in worldcat['contentRating']:
        wcrating = worldcat['contentRating'].lower().replace('tv', '').replace(':', '').replace('.', '')
        if 'y' in wcrating:
            map_rate['text'] = 'This program is designed to be appropriate for all children'
            map_rate['audiance'] = 'g'
        if 'y7' in wcrating:
            map_rate['text'] = 'This program is designed for children age 7 and above.'
            map_rate['audiance'] = 'g'
        if 'g' in wcrating:
            map_rate['text'] = 'Most parents would find this program suitable for all ages.'
            map_rate['audiance'] = 'g'
        if 'pg' in wcrating:
            map_rate['text'] = 'This program contains material that parents may find unsuitable for younger children.'
            map_rate['audiance'] = 'g'
        if '14' in wcrating:
            map_rate['text'] = 'This program contains some material that many parents would find unsuitable for children under 14 years of age.'
            map_rate['audiance'] = 'd'
        if 'ma' in wcrating:
            map_rate['text'] = 'This program is specifically designed to be viewed by adults and therefore may be unsuitable for children under 17.'
            map_rate['audiance'] = 'e'

    return map_rate

def main_title(data):
    main = data.split(':')
    main = main[0].strip()
    return unidecode.unidecode(main)

def sub_title(data):
    sub = data.split(':')
    return_sub = ''
    if len(sub) > 1:
        return_sub = sub[1].strip()
    return unidecode.unidecode(return_sub)

def string_cleanup(data):
    clean_str = str(data).encode('utf-8')
    clean_str = clean_str[3:]
    clean_str = clean_str[:-2]
    if clean_str == '':
        clean_str = str(data).encode('utf-8')
    return clean_str

def get_currentRole(data):
    return unidecode.unidecode(unicode(data.currentRole)) or u''

def get_notes(data):
    return unidecode.unidecode(unicode(data.notes)) or u''

def structured_notes(start_text, data):
    if len(data) > 1 and start_text != 'Cast' and start_text != 'SFX':
        start_text = start_text + 's'
    note_field = start_text + ': '
    for people in data:
        if start_text == 'Cast':
            note_field = note_field + unidecode.unidecode(people['name']) + ', ' + get_currentRole(people) + '; '
        else:
            note_field = note_field + unidecode.unidecode(people['name']) + '; '
    note_field = note_field[:-2]
    return note_field.strip()
    
def MARC245_c(IMDBvid):
    prod = "produced by "
    write = "written by "
    direct = "directed by "
    fin = ''

    if 'producer' in IMDBvid:
        for pp in producer:
            prod = prod + pp['name'] + ", "
        prod = prod[:-2]
        prod = prod.strip()
        fin = prod
        
    if 'writer' in IMDBvid:
        for ww in writer:
            write = write + ww['name'] + ", "
        write = write[:-2]
        write = write.strip()
        if len(fin) > 0:
            fin = fin + " ; " + write
        else:
            fin = write
            
    if 'writer' in IMDBvid:
        for dd in director:
            direct = direct + dd['name'] + ", "
        direct = direct[:-2]
        direct = direct.strip()
        if len(fin) > 0:
            fin = fin + " ; " + direct
        else:
            fin = direct
            
    return unidecode.unidecode(fin)

def set_008(date, pubyear, runTime, audiance, worldcatRecord):
    MARC008 = " ".ljust(40)
    LIST008 = list(MARC008)
    date = list(date)
    pubyear = list(pubyear)
    runTime = str(runTime)
    if len(runTime) == 2:
        runTime = '0' + runTime
    if len(runTime) == 1:
        runTime = '00' + runTime
    runTime = list(runTime)
    LIST008[0] = date[0]
    LIST008[1] = date[1]
    LIST008[2] = date[2]
    LIST008[3] = date[3]
    LIST008[4] = date[4]
    LIST008[5] = date[5]
    LIST008[6] = 'p'
    LIST008[7] = pubyear[0]
    LIST008[8] = pubyear[1]
    LIST008[9] = pubyear[2]
    LIST008[10] = pubyear[3]
    LIST008[15] = 'x'
    LIST008[16] = 'x'
    LIST008[17] = 'u'
    if hasattr(worldcatRecord, 'dcid'):
        if len(worldcatRecord['dcid']) > 0:
            dcid = worldcatRecord['dcid'][0].split()
            LIST008[15] = dcid[0]
            LIST008[16] = dcid[1]
            LIST008[17] = dcid[2]
    LIST008[18] = runTime[0]
    LIST008[19] = runTime[1]
    LIST008[20] = runTime[2]
    LIST008[22] = audiance
    LIST008[33] = 'v'
    LIST008[34] = 'l'
    if hasattr(worldcatRecord, 'materialType'):
        if len(worldcatRecord['materialType']) > 0:
            if 'partial animation' in worldcatRecord['materialType'].lower():
                LIST008[34] = 'c'
            elif 'animation' in worldcatRecord['materialType'].lower():
                LIST008[34] = 'a'
    LIST008[35] = 'e'
    LIST008[36] = 'n'
    LIST008[37] = 'g'
    if len(worldcatRecord['language']) > 0:
        lang = lanugage_lookup(worldcatRecord['language'][0])
        LIST008[35] = lang[0]
        LIST008[36] = lang[1]
        LIST008[37] = lang[2]
    LIST008[39] = 'c'
    
    return "".join(LIST008)

def set_264(worldcatRecord, year):
    v264 = []
    if worldcatRecord['placeOfPublication'] > 0:
        for location in worldcatRecord['placeOfPublication']:
            v264.append('a')
            v264.append(unidecode.unidecode(location).strip() + ';')
    else:
        v264.append('[Unknown];')

    if worldcatRecord['publisher'] > 0:
        for pub in worldcatRecord['publisher']:
            v264.append('b')
            v264.append(unidecode.unidecode(pub).strip() + ',')
    else:
        v264.append('[Unknown],')

    v264.append('c')
    v264.append(year + '.')
    return v264

def format_505(epi):
    v505 = []
    i = 0
    while i < len(epi):
        i += 1
        v505.append('g')
        v505.append('Episode ' + str(i) + ':')
        v505.append('t')
        if i < len(epi):
            v505.append(unidecode.unidecode(epi[i]['title']) + ' --')
        else:
            v505.append(unidecode.unidecode(epi[i]['title']))

    return v505

def vid_list(data):
    vid = {'IMDB': '',
	    'OCLC': '',
	    'UPC' : '',
	    'Price' : '$39.99',
	    'Season' : 1}
    
    vid['IMDB'] = data[0]
    vid['UPC'] = data[1]
    if len(data) == 3:
        vid['Price'] = data[2]
    if len(data) == 4:
        vid['Season'] = int(data[3])
    if '|' in data[0]:
        temp = data[0].split('|')
        vid['IMDB'] = temp[0]
        vid['OCLC'] = temp[1]
    return vid

def get_plot(IMDBvid, worldcatRecord):
    vPlot = ''
    if 'plot outline' in IMDBvid:
        vPlot = str(IMDBvid['plot outline'])
    if len(worldcatRecord['summery']) > 0:
        if len(worldcatRecord['summery'][0]) > vPlot:
            vPlot = worldcatRecord['summery'][0]
    return vPlot

def get_runtime(IMDBvid, se):
    vRuntime = '   '
    if hasattr(IMDBvid, 'runtimes'):
        if isinstance(IMDBvid['runtimes'],list):
            IMDBvid['runtimes'] = IMDBvid['runtimes'][0]
        vRuntime = string_cleanup(IMDBvid['runtimes'])
    
    if IMDBvid['kind'] == 'tv series':
    	vRuntime = len(IMDBvid['episodes'][se]) * 25

    return vRuntime

with open("videos.txt") as f:
    reader = csv.reader(f)
    video_list = list(reader)


for video in video_list:
    video_info = vid_list(video)
    print video_info['IMDB']
    #Set Variables
    record = Record()
    IMDBinfo = IMDb()
    worldcatRecord = OCLCScraper(video_info['OCLC'])
    IMDBvid = IMDBinfo.get_movie(video_info['IMDB'])
    if str(IMDBvid['kind']) == 'tv series':
        IMDBinfo.update(IMDBvid, 'episodes')
    vRuntime = get_runtime(IMDBvid,video_info['Season'])
    ratingGuide = rating_text(find_mpaa(IMDBvid), worldcatRecord)

    #001
    record.add_ordered_field(Field(tag = '001',data = "u"+ video_info['UPC']))
    #007
    record.add_ordered_field(Field(tag = '007',data = worldcatRecord['007']))
    #008
    record.add_ordered_field(Field(tag = '008',data = set_008(today.strftime('%y%m%d'), str(IMDBvid['year']), vRuntime, ratingGuide['audiance'], worldcatRecord)))
    #020 - Price and ISBN info
    record.add_ordered_field(Field(tag = '020',indicators = [' ',' '],subfields = ['c', video_info['Price'] ]))
    if hasattr(worldcatRecord, 'isbn'):
        if len(worldcatRecord['isbn']) > 0:
            for isbn in worldcatRecord['isbn']:
                record.add_ordered_field(Field(tag = '020',indicators = [' ',' '],subfields = ['a', isbn ]))
    #024 - UPC
    record.add_ordered_field(Field(tag = '024',indicators = ['1',' '],subfields = ['a', video_info['UPC'] ]))
    #035 - OCLC Number if it exists and the IMDb ID
    record.add_ordered_field(Field(tag = '024',indicators = [' ',' '],subfields = ['a', '(IMDb)tt' + IMDBvid.movieID ]))
    if video_info['OCLC'] != '':
        record.add_ordered_field(Field(tag = '035',indicators = [' ',' '],subfields = ['z', '(OCoLC)' + video_info['OCLC']]))
    #040 - Original Cataloging Information (KPL)
    record.add_ordered_field(Field(tag = '040',indicators = [' ',' '],subfields = ['a', OCLCSymble ,'b', lanugage_lookup(worldcatRecord['language'][0]) ,'c', OCLCSymble , 'e', 'rda' ]))
    #082 - Dewey number from worldcat 
    if len(worldcatRecord['dewey']) > 0:
        record.add_ordered_field(Field(tag = '082',indicators = ['0','0'],subfields = ['a', worldcatRecord['dewey']]))
    #245 - Main Title Info
    if sub_title(IMDBvid['title']) != '':
        record.add_ordered_field(Field(tag = '245',indicators = ['1','0'],subfields = ['a', main_title(IMDBvid['title']),'h', worldcatRecord['GMD'] + ' :','b', sub_title(IMDBvid['title']) + ' /' , 'c', MARC245_c(IMDBvid) + '.' ]))
    else:
        record.add_ordered_field(Field(tag = '245',indicators = ['1','0'],subfields = ['a', main_title(IMDBvid['title']), 'h', worldcatRecord['GMD'] + ' /','c', MARC245_c(IMDBvid) + '.' ]))
    #246 - Other names for the title
    if len(worldcatRecord['alternateName']) > 0:
        for altname in worldcatRecord['alternateName']:
            record.add_ordered_field(Field(tag = '246',indicators = ['3','1'],subfields = ['a', altname]))
    #264 - Production information from Worldcat
    record.add_ordered_field(Field(tag = '264',indicators = [' ','0'],subfields = set_264(worldcatRecord, str(IMDBvid['year']))))
    #300
    record.add_ordered_field(Field(tag = '300',indicators = [' ',' '],subfields = ['a', str(worldcatRecord['discs']) + ' ' + worldcatRecord['itemType'] + ' (' + str(vRuntime) + ' minutes) :','b', 'sound, ' + string_cleanup(str(IMDBvid['color info'])).lower() + ';' , 'c', '4 3/4 in.']))
    #336
    record.add_ordered_field(Field(tag = '336',indicators = [' ',' '],subfields = ['a', 'two-dimensional moving image','2', 'rdacontent']))
    #337
    record.add_ordered_field(Field(tag = '337',indicators = [' ',' '],subfields = ['a', 'video','2', 'rdamedia']))
    #338
    record.add_ordered_field(Field(tag = '338',indicators = [' ',' '],subfields = ['a', 'videodisc','2', 'rdacarrier']))
    #344
    record.add_ordered_field(Field(tag = '344',indicators = [' ',' '],subfields = ['a', 'digital','b', 'optical', 'g', 'surround', '2', 'rda']))
    #346
    record.add_ordered_field(Field(tag = '346',indicators = [' ',' '],subfields = ['b', 'NTSC', '2', 'rda']))
    #347
    record.add_ordered_field(Field(tag = '347',indicators = [' ',' '],subfields = ['a', 'video file','e','region 1', '2', 'rda']))
    #490 - Series Statement from Worldcat
    if len(worldcatRecord['series']) > 0:
        for series in worldcatRecord['series']:
            record.add_ordered_field(Field(tag = '490',indicators = ['0',' '],subfields = ['a', series]))
    #500 - General Notes from Worldcat and IMDb top 250 info
    if len(worldcatRecord['generalNotes']) > 0:
        for gennote in worldcatRecord['generalNotes']:
            record.add_ordered_field(Field(tag = '500',indicators = [' ',' '],subfields = ['a', gennote]))
    if 'top 250 rank' in IMDBvid:
        record.add_ordered_field(Field(tag = '500',indicators = [' ',' '],subfields = ['a', 'IMDb Top 250 Movies Ranking: ' + str(IMDBvid['top 250 rank'])]))
    #505 - TV Series Episodes
    if str(IMDBvid['kind']) == 'tv series':
        record.add_ordered_field(Field(tag = '505',indicators = ['0','0'],subfields = format_505(IMDBvid['episodes'][video_info['Season']])))
    #508 & 700/710 - Crew member notes and searchable 7xx fields
    if 'writer' in IMDBvid:
        record.add_ordered_field(Field(tag = '508',indicators = [' ',' '],subfields = ['a', structured_notes('Writer',IMDBvid['writer'])]))
    if 'producer' in IMDBvid:
        record.add_ordered_field(Field(tag = '508',indicators = [' ',' '],subfields = ['a', structured_notes('Producer',IMDBvid['producer'])]))
        for mProd in IMDBvid['producer']:
            record.add_ordered_field(Field(tag = '700',indicators = ['1',' '],subfields = ['a', invert_name(mProd) + ';','e','producer.']))
    if 'director' in IMDBvid:
        record.add_ordered_field(Field(tag = '508',indicators = [' ',' '],subfields = ['a', structured_notes('Director',IMDBvid['director'])]))
        for mDir in IMDBvid['director']:
            record.add_ordered_field(Field(tag = '700',indicators = ['1',' '],subfields = ['a', invert_name(mDir) + ';','e','director.']))
    if 'editor' in IMDBvid:
        record.add_ordered_field(Field(tag = '508',indicators = [' ',' '],subfields = ['a', structured_notes('Editor',IMDBvid['editor'])]))
        for mEdit in IMDBvid['editor']:
            record.add_ordered_field(Field(tag = '700',indicators = ['1',' '],subfields = ['a', invert_name(mEdit) + ';','e','editor.']))
    if 'cinematographer' in IMDBvid:
        record.add_ordered_field(Field(tag = '508',indicators = [' ',' '],subfields = ['a', structured_notes('Cinematographer',IMDBvid['cinematographer'])]))
        for mCin in IMDBvid['cinematographer']:
            record.add_ordered_field(Field(tag = '700',indicators = ['1',' '],subfields = ['a', invert_name(mCin) + ';','e','cinematographer.']))
    if 'music department' in IMDBvid:
        record.add_ordered_field(Field(tag = '508',indicators = [' ',' '],subfields = ['a', structured_notes('Musician',IMDBvid['music department'])]))
    if 'special effects companies' in IMDBvid:
        record.add_ordered_field(Field(tag = '508',indicators = [' ',' '],subfields = ['a', structured_notes('SFX',IMDBvid['special effects companies'])]))
        for mFX in IMDBvid['special effects companies']:
            if len(mFX.notes) > 0:
                record.add_ordered_field(Field(tag = '710',indicators = ['2',' '],subfields = ['a', str(mFX) + ' (Firm),', 'g', str(mFX.notes)]))
            else:
                record.add_ordered_field(Field(tag = '710',indicators = ['2',' '],subfields = ['a', str(mFX) + ' (Firm)']))
    #511 & 700 - Cast Notes and Searchable 700 Fields
    if 'cast' in IMDBvid:
        record.add_ordered_field(Field(tag = '511',indicators = ['1',' '],subfields = ['a', structured_notes('Cast',IMDBvid['cast'])]))
        for index, mAct in enumerate(IMDBvid['cast']):
            if len(mAct.currentRole) > 0:
                if len(mAct.notes) > 0 and 'uncredited' not in mAct.notes:
                    record.add_ordered_field(Field(tag = '700',indicators = ['1',' '],subfields = ['a', invert_name(mAct) + ';','e','actor.', 'g', get_currentRole(mAct) + ' ' + get_notes(mAct)]))
                elif len(mAct.notes) == 0:
                    record.add_ordered_field(Field(tag = '700',indicators = ['1',' '],subfields = ['a', invert_name(mAct) + ';','e','actor.', 'g', get_currentRole(mAct)]))
            else:
                record.add_ordered_field(Field(tag = '700',indicators = ['1',' '],subfields = ['a', invert_name(mAct) + ';','e','actor.']))
            if index == 10:
                #Stopping at the top 10 cast members,
                #or else the list will be too long to read
                break
    #520 - plot
    if get_plot(IMDBvid, worldcatRecord) != '':
        record.add_ordered_field(Field(tag = '520',indicators = [' ',' '],subfields = ['a', get_plot(IMDBvid, worldcatRecord)]))
    #520 - IMDB Rating
    if 'rating' in IMDBvid:
        record.add_ordered_field(Field(tag = '520',indicators = ['1',' '],subfields = ['a', 'IMDb Rating: ' + str(IMDBvid['rating']) + '/10']))
    #521 MPAA Rating
    record.add_ordered_field(Field(tag = '521',indicators = ['8',' '],subfields = ['a', ratingGuide['text']]))
    #538 - Technical Notes
    if len(worldcatRecord['technical']) > 0:
        record.add_ordered_field(Field(tag = '538',indicators = [' ',' '],subfields = ['a', worldcatRecord['technical']]))
    #540 - Use Notes
    record.add_ordered_field(Field(tag = '540',indicators = [' ',' '],subfields = ['a', 'For private home use only.']))
    #540 - Lanugate Notes
    if len(worldcatRecord['languageNotes']) > 0:
        record.add_ordered_field(Field(tag = '546',indicators = [' ',' '],subfields = ['a', worldcatRecord['languageNotes']]))
    #650 & 655 - Subject & Genre Headings
    if 'tv series' in str(IMDBvid['kind']):
        record.add_ordered_field(Field(tag = '655',indicators = [' ','0'],subfields = ['a', 'TV shows']))
        record.add_ordered_field(Field(tag = '650',indicators = [' ','0'],subfields = ['a', 'Television series']))
        record.add_ordered_field(Field(tag = '655',indicators = [' ','0'],subfields = ['a', 'Television programs']))
    if "movie" in str(IMDBvid['kind']):
        record.add_ordered_field(Field(tag = '655',indicators = [' ','0'],subfields = ['a', 'Feature films.']))
        for g in IMDBvid['genres']:
            if g == 'Sci-Fi':
                g = 'Science Fiction'
            if g == 'Family':
                record.add_ordered_field(Field(tag = '655',indicators = [' ','0'],subfields = ['a', "Children's films."]))
            else:
                record.add_ordered_field(Field(tag = '650',indicators = [' ','0'],subfields = ['a', g + ' films.']))
    if len(worldcatRecord['subjects']) > 0:
        for sh in worldcatRecord['subjects']:
            record.add_ordered_field(Field(tag = '650',indicators = [' ','0'],subfields = ['a', sh]))
    #856 - Artwork and IMDb Links
    record.add_ordered_field(Field(tag = '856',indicators = ['4',' '],subfields = ['u', IMDBvid['full-size cover url'], 'y', 'Artwork of ' + unidecode.unidecode(IMDBvid['title'])]))
    record.add_ordered_field(Field(tag = '856',indicators = ['4',' '],subfields = ['u', 'http://www.imdb.com/title/tt' + IMDBvid.movieID, 'y', 'IMDb Link']))
    #905 - Generator Notes
    record.add_ordered_field(Field(tag = '905',indicators = [' ',' '],subfields = ['a', 'This record was generated by the IMDb + OCLC to Marc Python Script', 'v', version]))
    #Set leader info
    l = list(record.leader)
    l[5] = 'n'
    l[6] = 'g'
    l[7] = 'a'
    l[17] = '1'
    l[18] = 'i'
    record.leader = "".join(l)
    #print record #for troubleshooting
    MARCFile = open(FILENAMEVAR, 'a')
    MARCFile.write(record.as_marc())
    MARCFile.close()
