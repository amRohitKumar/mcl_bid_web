"""
compares the bidder undertaking with the original undertaking format 
returns the similarity value
"""
import mcl_utils as mclu
import spacy
import en_core_web_md

def extract_gtc(gtc_path):
    gtc, _, __ = mclu.open_file_link(gtc_path)
    return gtc[58].get_text()

def compare_genuineness(filepath, gtc_undertaking):
    bidder_undertaking = mclu.extract_text(filepath, endpg=1)
    nlp = en_core_web_md.load() 
    # can change to en_core_web_md or en_core_web_md if problem in downloading
    rel = mclu.get_answer(bidder_undertaking,
                          "does the company have any relative in mcl in yes or no?",
                          cleaning_text=None)
    if "yes" in rel:
        rel = True
    else:
        rel = False
    sim = nlp(bidder_undertaking).similarity(nlp(gtc_undertaking))
    return {
        "any relatives": rel,
        "similarity": sim
    }

def extract_local_content(filepath):
    filetext = mclu.extract_text(filepath)
    local_content = mclu.get_answer(filetext, 
                                    "amount of local content",
                                    cleaning_text=r"(\d+)%")
    local_content = int(local_content)
    if local_content > 50:
        return "Class 1 Supplier"
    elif local_content > 20:
        return "Class 2 Supplier"
    else:
        return "Not Eligible"