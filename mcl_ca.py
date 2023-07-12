import mcl_utils as mclu
import re
import pandas as pd

def extract_from_CA(filepath):
  filetext = mclu.extract_text(filepath, endpg=1)
  ca = mclu.get_answer(filetext, "name of the CA firm")

  udin = re.findall(r"UDIN[:; -]*([0-9A-Z ]*)", filetext)[0].replace(" ", "")
  
  audited = mclu.get_answer(filetext, "name of the company audited")
  turnover = re.findall(r"20[\d][\d][ ]*-[ ]*20[\d][\d][ ]*([0-9.]+[,]?[0-9.]*)[ ]*", filetext)
  year = re.findall(r"(20[\d][\d][ ]*-[ ]*20[\d][\d])[ ]*[0-9.]+[ ]*", filetext)
  relevant_work = pd.DataFrame({"Financial Year": year,
                                "Gross Turn Over": turnover})
  relevant_work["Gross Turn Over"] = relevant_work["Gross Turn Over"].str.replace(",", "")
  relevant_work["Gross Turn Over"] = relevant_work["Gross Turn Over"].astype("float64")
  work_type = mclu.get_answer(filetext, "type of work done by the company audited by " + ca)
  info_extracted = {
      "CA Name": ca,
      "UDIN No.": udin,
      "Company audited": audited,
      "Relevant Work Experience": relevant_work,
      "Type of work done": work_type
  }
  return info_extracted