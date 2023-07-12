import os
import re
import mcl_utils as mclu

def getPAN(imagepath):
  potential_changes = {"S": "5", "I": "1", "O": "0", "Z": "2",
                       "B": "8", "T": "7", "A": "4", "l": "1"}
  images = mclu.pdf2img(imagepath)
  pan = set()
  
  for img in images:
    text = mclu.extract_text_easyocr(img)
    os.remove(img)
    found1 = False
    for txt in text:
      for t in txt.split():
        if len(t) == 10:
          dig = t[-5: -1]
          dig_changed = ""
          for d in dig:
            if d.isalpha() and d in potential_changes.keys():
              dig_changed += potential_changes[d]  # compensating for bad image quality that causes poor character recognition
              # this still does not eliminate the whole problem... it still may not work in some cases
            else:
              dig_changed += d
          t = t[: -5] + dig_changed + t[-1]
          t = re.findall(r"[A-Z][A-Z][A-Z][A-Z][A-Z][0-9][0-9][0-9][0-9][A-Z]", t)
          if len(t) != 0 and found1 == False:
            found1 = True
            pan.add(t[0])
    
  return list(pan)

