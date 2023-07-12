import mcl_utils as mclu
import time


def extract_from_legal(filepath):
    output = {}
    filetext = mclu.extract_text(filepath, endpg=4)
    jv = mclu.get_answer(filetext, "is the operation a joint venture/consortium in yes or no",
                         cleaning_text=None)

    if "yes" in jv.lower():
        date = mclu.get_answer(
            filetext, "joint venture formation date in dd/mm/yyyy format.")
        time.sleep(35)
        jv_name = mclu.get_answer(
            filetext, "name of the joint venture/consortium")
        companies = mclu.get_answer(filetext,
                                    "name of the companies in the joint venture",
                                    number="all")

        for i in range(len(companies)):
            companies[i] = companies[i].replace("$", "").strip()

        partnership = {}
        lead = companies[0]
        for c in companies:
            time.sleep(35)
            share = mclu.get_answer(filetext,
                                    "partnership share of " + c + " in the joint venture/consortium",
                                    cleaning_text=r"([0-9]+)[ ]*[%]")
            share = int(share)/100
            partnership[c] = share
        for c in companies:
            if partnership[lead] < partnership[c]:
                lead = c
        output = {
            "JV": True,
            "name": jv_name,
            "formation date": date,
            "partners": partnership,
            "lead": lead
        }

    else:
        company = mclu.get_answer(
            filetext, "name of the company in the operation")
        date = mclu.get_answer(
            filetext, "company formation date in dd/mm/yy format")
        output = {
            "JV": False,
            "name": company,
            "formation date": date,
            "partners": {company: 1},
            "lead": company
        }
        time.sleep(30)
    return output
