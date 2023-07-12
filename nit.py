import re
import camelot as cam

class CMCNITDoc: 
    doc = None
    doc_df=[]
    def __init__(self, filepath) -> None:
        self.doc = cam.read_pdf(filepath, 
                                pages = 'all')[:2]
        for i in range(len(self.doc)):
            self.doc_df.append(self.doc[i].df)
            self.doc_df[i].drop(self.doc_df[i].index[0], inplace=True)
            
    def extract_dates(self, particular):
        self.doc_df[1][1] = self.doc_df[1][1].str.lower()
        x = self.doc_df[1].loc[self.doc_df[1][1]==particular]
        return x[2].to_string().split("  ")[-1]
        
    def extract_info(self):
        work_desc=self.doc_df[0]
        cost = work_desc.loc[1, 1] 
        # changed 'Estimated Cost of \nWork \n  (In Rs.)' to 1
        cost = float(re.sub(r"[₹RrSs, /-]", "", cost).split()[0])
        completion = int(work_desc.loc[1, 2].split()[0]) 
        # changed 'Period of \nCompletion \n(In Days)' to 2
        desc = re.sub(r"\n", "", work_desc.loc[1, 0])
        # changed "Description of work" to 0
        
        return {
            "Cost of Work": cost,
            "Period of Completion (Days)": completion,
            "Work Description": desc,
            "Bid Start Date": self.extract_dates("bid submission start date"),
            "Bid End Date": self.extract_dates("bid submission end date"),
            "Tender Publication Data": self.extract_dates('tender e-publication date')
        }
    
class CivilNITDoc:
    doc = None
    doc_df=[]
    def __init__(self, filepath) -> None:
        self.doc = cam.read_pdf(filepath, 
                                pages = 'all')
        
        self.doc_df.append(self.doc[0].df)
        self.doc_df[0].drop(self.doc_df[0].index[0], inplace=True)
        
        self.doc_df.append(self.doc[2].df)
        self.doc_df[1].drop(self.doc_df[1].index[0], inplace=True)
        
    def extract_dates(self, particular):
        self.doc_df[1][1] = self.doc_df[1][1].str.lower()
        # changed 'Particulars' to 1
        x = self.doc_df[1].loc[self.doc_df[1][1]==particular]
        # changed 'Particulars' to 1
        return x[2].to_string().split("  ")[-1]
        # changed 'Date' to 2
        
    def extract_info(self):
        work_desc=self.doc_df[0]
        cost = work_desc.loc[1, 2] 
        cost = float(re.sub(r"[₹RrSs, /-]", "", cost).split()[0])
        completion = int(work_desc.loc[1, 3].split()[0]) 
        # changed 'Period of \nCompletion \n(In Days)' to 2
        desc = re.sub(r"\n", "", work_desc.loc[1, 0])
        # changed "Description of work" to 0
        
        return {
            "Cost of Work": cost,
            "Period of Completion (Days)": completion,
            "Work Description": desc,
            "Bid Start Date": self.extract_dates("bid submission start date"),
            "Bid End Date": self.extract_dates("bid submission end date"),
            "Tender Publication Data": self.extract_dates('tender e-publication date')
        }