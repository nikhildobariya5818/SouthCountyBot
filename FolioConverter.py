import re

def completeFolioForMiami(str):
    str = str.replace('-','')
    if len(str) == 12:
        return "0"+str
    elif len(str) == 13:
        return str
    return str

def completeFolioForBroward(str):
    str = str.replace('-','')
    if len(str) == 11:
        return "0"+str
    elif len(str) == 12:
        return str
    return str

def FolioForMiami(input_string):
    input_string = completeFolioForMiami(input_string)
    pattern = r'(\d{2})(\d{4})(\d{3})(\d{4})'
    replacement = r'\1-\2-\3-\4'
    formatted_string = re.sub(pattern, replacement, input_string)
    return formatted_string

def FolioForBroward(input_string):
    input_string = completeFolioForBroward(input_string)
    pattern = r'(\d{4})(\d{2})(\d{2})(\d{4})'
    replacement = r'\1-\2-\3-\4'
    formatted_string = re.sub(pattern, replacement, input_string)
    return formatted_string