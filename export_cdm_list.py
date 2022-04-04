import CdmApi
import json
from config import CDM_REF_BASE, CDM_IIIF_BASE

#requests_cache.install_cache('requests_che')


def sanitize(val):
    '''
    clean up Cdm field value. Somehow empty values are {} in the json output

    :param val: String
    :return:
    '''
    # sanitizer for empty fields
    txt = ''
    if not isinstance(val, dict):
        txt = val.replace(';;', ';')
    return txt


def convert(metadata, pagemetadata):
    '''
    convert Cdm metadata values to klokan values

    :param metadata: dict
    :param pagemetadata: dict
    :return: csv row Dict
    '''
    # convert to csv row
    row = {}

    ubvuid = sanitize(pagemetadata['lok001']) if pagemetadata else sanitize(metadata['lok001'])
    row['id'] = ubvuid
    dmrecord = pagemetadata['dmrecord'] if pagemetadata else metadata['dmrecord']
    row['dmrecord'] = dmrecord
    row['link'] = '%s%s' % (CDM_REF_BASE, dmrecord)
    row['iiif'] = '%s%s' % (CDM_IIIF_BASE, dmrecord)
    #row['title'] = '%s, uit: %s' % (pagemetadata['title'], metadata['title']) if pagemetadata else metadata['title']

    if ubvuid == '':
        row = False
    return row


# Get all record ptrs
nick = 'krt'
ptrs = CdmApi.getAllPtr(nick)

data=[]

# loop through ptrs and get metadata
for ptr in ptrs:
    print(ptr)
    metadata = CdmApi.getMetadata(nick, ptr)
    if 'code' not in metadata:  # some broken items?
        if CdmApi.isCpd(nick, ptr):
            cpd = CdmApi.getCpdPages(nick, ptr)
            n = 0
            if cpd['type'] != 'Monograph':
                for page in cpd['page']:
                    pageptr = page['pageptr']
                    page_metadata = CdmApi.getMetadata(nick, pageptr)
                    row = convert(metadata, page_metadata)
                    if row:
                        data.append(row)
            else:
                for node in cpd['node']['node']:  # specific case of tmk, could be deeper
                    if type(node['page']) is dict:  # what a shitty data structure
                        print('***dict!***')
                        print(cpd)
                        page = node['page']
                        pageptr = page['pageptr']
                        page_metadata = CdmApi.getMetadata(nick, pageptr)
                        row = convert(metadata, page_metadata)
                        if row:
                            data.append(row)
                    else:
                        print('***NOT dict!***')
                        print(cpd)
                        for page in node['page']:
                            pageptr = page['pageptr']
                            page_metadata = CdmApi.getMetadata(nick, pageptr)
                            row = convert(metadata, page_metadata)
                            if row:
                                data.append(row)
        else:
            row = convert(metadata, False)
            if row:
                data.append(row)


with open('cdm_export.json', 'w') as f:
    json.dump(data, f, indent=4, sort_keys=True)