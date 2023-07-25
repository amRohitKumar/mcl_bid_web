import mcl_utils as mclu
import spacy
import en_core_web_md


def extract_attorney_desc(filepath, nit_desc):
    filetext = mclu.extract_text(filepath)
    attorney = mclu.get_answer(filetext, "name of the legal attorney")
    bidder_desc = mclu.get_answer(filetext, "description of the work")

    nlp = en_core_web_md.load()
    nit = nlp(nit_desc)
    bidder = nlp(bidder_desc)
    sim = nit.similarity(bidder)
    output = {
        "attorney": attorney,
        "work similarity": sim
    }
    return output
