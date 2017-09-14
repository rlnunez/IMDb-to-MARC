import requests
from lxml import html
from xml.etree import ElementTree as ET
import rdflib
from rdflib import URIRef, Namespace, RDF, Graph, Literal, BNode, plugin, Variable

def get_labels(graph, uri, predicate_string):
    predicate = rdflib.term.URIRef(u'http://schema.org/' + predicate_string)
    name = rdflib.term.URIRef(u'http://schema.org/name')
    object_list = []
    for obj in graph.objects(uri, predicate):
        label = obj
        if graph.value(obj, name):
            label = graph.value(obj, name)
        object_list.append(label)
    object_labels = object_list
    return(object_labels)

def getBibframe(OCLCnum,predicate):
    # set default uri and predicates
    uri = rdflib.term.URIRef(u'http://www.worldcat.org/oclc/' + OCLCnum)
    # create an in-memory RDF graph for the resource named in uri
    graph = rdflib.Graph()
    graph.parse(uri)
    # for each of the strings in the predicates list ...
    return get_labels(graph,uri,predicate)

def OCLCScraper(OCLCNum):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',}
    worldcatRecord = {'title' : '',
                      'placeOfPublication' : '',
                      'publisher' : '',
                      'yearPublished' : '',
                      'itemType' : '',
                      'summery' : '',
                      'genre' : '',
                      'languageNotes' : '',
                      'OCLCNumber' : '',
                      'generalNotes' : '',
                      'language' : '',
                      'contentRating' : '',
                      'subjects' : '',
                      'dcid' : '',
                      'isbn' : '',
                      'technical' : '',
                      'materialType' : '',
                      'alternateName' : '',
                      'awards' : '',
                      'series' : ''}
    if OCLCNum == '':
      return worldcatRecord
    worldcatRecord['OCLCNumber'] = OCLCNum
    requestURL = 'https://www.worldcat.org/oclc/' + OCLCNum
    r = requests.get(requestURL, headers=headers)
    tree = html.fromstring(r.content)
    worldcatRecord['title'] = getBibframe(OCLCNum,'name')[0]
    worldcatRecord['summery'] = getBibframe(OCLCNum,'description')
    PubInfo = tree.xpath('//td[@id="bib-publisher-cell"]/text()')[0]
    worldcatRecord['itemType'] = tree.xpath('//span[@class="itemType"]/text()')[0]
    worldcatRecord['generalNotes'] = tree.xpath('//tr[@class="details-notes"]/td/text()')
    worldcatRecord['dcid'] = tree.xpath('//span[@property="dcterms:identifier"]/text()')
    worldcatRecord['isbn'] = tree.xpath('//span[@property="schema:isbn"]/text()')
    worldcatRecord['placeOfPublication'] = PubInfo.split(':')[:-1]
    worldcatRecord['publisher'] = PubInfo.split(':')[-1].split(',')[:-1]
    worldcatRecord['yearPublished'] = getBibframe(OCLCNum,'datePublished')
    worldcatRecord['language'] = getBibframe(OCLCNum,'inLanguage')
    worldcatRecord['genre'] = getBibframe(OCLCNum,'genre')
    worldcatRecord['contentRating'] = getBibframe(OCLCNum,'contentRating')
    worldcatRecord['subjects'] = getBibframe(OCLCNum,'about')
    worldcatRecord['alternateName'] = getBibframe(OCLCNum,'alternateName')
    worldcatRecord['awards'] = getBibframe(OCLCNum,'awards')
    worldcatRecord['series'] = getBibframe(OCLCNum,'isPartOf')

    datailsTable = tree.xpath('//div[@id="details"]//table//tr')
    for rows in datailsTable:
        if rows.xpath('th/text()')[0][:-1].lower() == 'language note':
            worldcatRecord['languageNotes'] = rows.xpath('td/text()')[0]
        elif rows.xpath('th/text()')[0][:-1].lower() == 'notes':
            worldcatRecord['generalNotes'] = htmlbr_tolist(rows.xpath('td')[0])
        elif rows.xpath('th/text()')[0][:-1].lower() == 'details':
            worldcatRecord['technical'] = rows.xpath('td/text()')[0]
        elif rows.xpath('th/text()')[0][:-1].lower() == 'material type':
            worldcatRecord['materialType'] = rows.xpath('td/text()')[0]
    
    return worldcatRecord

def htmlbr_tolist(data):
    pushlist = []
    pushlist.append(data.xpath('text()'))
    temp = data.xpath('//br/text()')
    for push in temp:
        pushlist.append(push)
    return pushlist
