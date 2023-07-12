import mcl_utils as mclu

def extract_attorney(filepath):
    filetext = mclu.extract_text(filepath, endpg=1)
    return mclu.get_answer(filetext, "name of the person with power of attorney")
    
# extract_attorney("https://res.cloudinary.com/dauxdhnsr/image/upload/v1686230093/POWEROFATTORNEYARUNVERMA2021_on0z1f.pdf")