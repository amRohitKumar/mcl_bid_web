import mcl_utils as mclu


def extract_from_dsc(filepath):
    filetext = mclu.extract_text(filepath)
    return mclu.get_answer(filetext,
                           "name of the person with power of attorney")
