import CdmApi
import requests_cache, json

requests_cache.install_cache('requests_cache')
# 3557: landgoedkaarten
# 6743, 2131: tmk
# Globes: 3748, 3769, 3727, 3832, 3866, 3811, 3853, 3790,3618,3794
IGNORE_LIST = [3748, 3769, 3727, 3832, 3866, 3811, 3853, 3790,
               3618, 3794]  # compound or single records that should be skipped
IGNORE_PAGE_TITLE_LIST = ['[indexkaart]']
NO_DEEPZOOM = [7244]
REF_BASE = 'https://vu.contentdm.oclc.org/digital/collection/krt/id/'
IIIF_BASE = 'https://vu.contentdm.oclc.org/digital/iiif/krt/'
#DZ_BASE = 'http://imagebase.ubvu.vu.nl/cdm/deepzoom/collection/krt/id/'


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
    row['link'] = '%s%s' % (REF_BASE, dmrecord)
    row['iiif'] = '%s%s' % (IIIF_BASE, dmrecord)
    #row['title'] = '%s, uit: %s' % (pagemetadata['title'], metadata['title']) if pagemetadata else metadata['title']

    if (pagemetadata and pagemetadata['title'].lower() in IGNORE_PAGE_TITLE_LIST) or ubvuid == '':
        row = False

    return row


# Get all record ptrs
nick = 'krt'
ptrs = CdmApi.getAllPtr(nick)

data=[]

# loop through ptrs and get metadata
for ptr in ptrs:
    print(ptr)
    if ptr not in IGNORE_LIST:
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
                            page = node['page']
                            pageptr = page['pageptr']
                            page_metadata = CdmApi.getMetadata(nick, pageptr)
                        row = convert(metadata, page_metadata)
                        if row:
                            data.append(row)
                        else:
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