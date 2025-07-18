"""
Translates files from .NTXT, exported from CAESAR II, to a format readable in PEPS.

Current PEPS cards implemented:
- CROS
- TANG
- BRAD
- VALV
- CRED
- ERED
- SUPP
"""
import os
from datetime import datetime as time
import pandas as pd

class Base:
    """
    .NTXT file object.
    """
    def __init__(self, log_text=""):
        self.path = os.getcwd()
        self.log = self.path + "/sup_info.log"
        self.counter = 0
        self.file_list = []

        if log_text != "":
            self.log = log_text
        self.counter += 1
        self.append_log("> Base class created...")

    def append_log(self, log_text):
        """Log function."""
        t_now = time.now()
        t_stamp = f"{t_now.hour}.{t_now.minute}.{t_now.second} "
        otext  = t_stamp + log_text
        f_log = open(self.log, "a",encoding="utf-8")
        f_log.write(otext + "\n")
        f_log.close()
        print(otext)
    
    def get_file_list(self):
        """
        Creates list with file objects on parent folder.

        Syntax: [[file_name,extension]]
        """
        file_list = self.file_list[:]

        with os.scandir(self.path) as entries:
            for entry in entries:
                entry_name = entry.name
                file_list.append(entry_name.split("."))
        
        return file_list

class NtxtObj(Base):
    """
    .NTXT file object.
    """
    def __init__(self, log_text=""):
        super().__init__(log_text)
        self.ntxt_file_list = []
        self.append_log("> NtxtObj class created...")
    
    def list_ntxt_files(self):
        """Lists .NTXT files from parent folder."""
        file_list = self.get_file_list()
        ntxt_file_list = []
        
        for file_name in file_list:
            if file_name[1] == "ntxt":
                self.append_log(">>> .NTXT file [" + str(len(ntxt_file_list)) + "] --> " + file_name[0])
                ntxt_file_list.append(file_name[0])

        return ntxt_file_list
    
    def choose_ntxt(self):
        """Allows user to choose .NTXT file to translate."""
        ntxt_file_list = self.list_ntxt_files()

        if len(ntxt_file_list) > 1:
            self.append_log(">>> Input .NTXT file to translate:")
            user_ntxt = input()
        else:
            user_ntxt = 0

        self.append_log(">>> Read file [" + str(user_ntxt) +"]")
        return(self.path + "/" + ntxt_file_list[int(user_ntxt)] + ".NTXT")
    
    def read_ntxt(self):
        """
        Reads .NTXT file and creates .NTXT file object.
        """
        cols = ["type", "blank space", "init node n", "final node n", "x disp", "y disp", "z disp", "ext diam", "thick"]
        ntxt_dataframe = pd.read_fwf(self.choose_ntxt(), header=None, names=cols, widths=[4,5,10,10,10,10,10,10,10],comment="*",skipfooter=3)
        ntxt_dataframe = ntxt_dataframe.drop(["blank space"], axis=1)
        ntxt_dataframe = ntxt_dataframe.drop(ntxt_dataframe[(ntxt_dataframe["type"]!="ELMT") & (ntxt_dataframe["type"]!="REST") & (ntxt_dataframe["type"]!="RIGD") & (ntxt_dataframe["type"]!="BEND") & (ntxt_dataframe["type"]!="RED")].index)
        ntxt_dataframe = ntxt_dataframe.reset_index()
        ntxt_dataframe = ntxt_dataframe.drop(["index"], axis=1)

        return ntxt_dataframe

class PepsObj(NtxtObj):
    """
    PEPS file object.
    """
    def __init__(self, log_text=""):
        super().__init__(log_text)
        self.peps_file = self.path + "/output.FRE"
        self.append_log("> PepsObj class created...")
        self.append_log("> " + self.peps_file.split("/")[1] + " file created...")

        # List of CROS cards.
        self.ntxt_dataframe = self.read_ntxt().copy(deep=True)
        self.cros_cards = self.ntxt_dataframe["ext diam"].dropna().index.tolist()

        # Fill elements cards.
        self.element_cards = self.ntxt_dataframe.index.to_list()

    def append_peps(self, peps_text):
        """Write function."""
        f_peps = open(self.peps_file, "a",encoding="utf-8")
        f_peps.write(peps_text)
        f_peps.close()

    def undo_peps(self):
        """Delete line function."""
        f_peps = open(self.peps_file, "r+",encoding="utf-8")
        f_peps.seek(0, os.SEEK_END)
        pos = f_peps.tell() - 1
        while pos > 0 and f_peps.read(1) != "\n":
            pos -= 1
            f_peps.seek(pos, os.SEEK_SET)
        if pos > 0:
            f_peps.seek(pos, os.SEEK_SET)
            f_peps.truncate()
        f_peps.close()
    
    def translate_to_peps_file(self):
        """
        Translates .NTXT file into .FRE.
        """
        peps_dataframe = pd.DataFrame(columns=["IDEN", "NODE", "DX", "DY", "DZ", "RA", "OD", "CD"])

        # Clear output.FRE file, if exists.
        try:
            f_peps = open(self.peps_file, "w",encoding="utf-8")
            f_peps.close()
            self.append_log("> " + self.peps_file.split("/")[1] + " file cleared...")
        except Exception as clear_output_error:
            self.append_log("> ERROR: Couldn't clear " + self.peps_file.split("/")[1] + " file!")
            return clear_output_error

        self.append_log("> Translation job started...")

        peps_dataframe.loc[-1,"IDEN"] = "ANCH"
        peps_dataframe.loc[-1,"NODE"] = "10"

        for item in self.element_cards:
            if self.ntxt_dataframe["type"].iloc[item] == "ELMT":

                if item in self.cros_cards:
                    peps_dataframe.loc[item-0.5,"IDEN"] = "CROS"
                    peps_dataframe.loc[item-0.5,"CD"] = 100 + self.cros_cards.index(item)

                for entry in self.ntxt_dataframe["final node n"].head(item).str.contains(self.ntxt_dataframe["init node n"].loc[item]):
                    if entry is True:
                        peps_dataframe.loc[item-0.25,"IDEN"] = "JUNC"
                        peps_dataframe.loc[item-0.25,"NODE"] = self.ntxt_dataframe["init node n"].iloc[item].split(".")[0]

                peps_dataframe.loc[item,"IDEN"] = "TANG"
                peps_dataframe.loc[item,"NODE"] = self.ntxt_dataframe["final node n"].iloc[item].split(".")[0]
                peps_dataframe.loc[item,"DX"] = self.ntxt_dataframe["x disp"].iloc[item]
                peps_dataframe.loc[item,"DY"] = self.ntxt_dataframe["y disp"].iloc[item]
                peps_dataframe.loc[item,"DZ"] = self.ntxt_dataframe["z disp"].iloc[item]
                peps_dataframe.loc[item,"OD"] = self.ntxt_dataframe["ext diam"].iloc[item]

            elif self.ntxt_dataframe["type"].iloc[item] == "REST":
                if self.ntxt_dataframe["init node n"].iloc[item] != "10.0000":
                    peps_dataframe.loc[item,"IDEN"] = "SUPP"
                    peps_dataframe.loc[item,"NODE"] = self.ntxt_dataframe["init node n"].iloc[item].split(".")[0]
                    peps_dataframe.loc[item,"DZ"] = "1"
            elif self.ntxt_dataframe["type"].iloc[item] == "RIGD":
                peps_dataframe.loc[item-1,"IDEN"] = "VALV"
            elif self.ntxt_dataframe["type"].iloc[item] == "BEND":
                peps_dataframe.loc[item-1,"NODE"] = int(peps_dataframe.loc[item-1,"NODE"]) - 2
                peps_dataframe.loc[item,"NODE"] = int(peps_dataframe.loc[item-1,"NODE"]) + 2
                peps_dataframe.loc[item,"IDEN"] = "BRAD"
                peps_dataframe.loc[item,"RA"] = self.ntxt_dataframe["init node n"].iloc[item]
            
            try:
                if item in self.cros_cards:
                    if peps_dataframe["CD"].loc[item-0.5] != 100:
                        if pd.isna(peps_dataframe.loc[item,"DZ"]) is True:
                            peps_dataframe.loc[item,"IDEN"] = "CRED"
                        else:
                            peps_dataframe.loc[item,"IDEN"] = "ERED"
            except:
                continue

        # Remove unwanted JUNCs.
        peps_dataframe = peps_dataframe.reset_index()
        peps_dataframe = peps_dataframe.drop(["index"],axis=1)
        peps_dataframe = peps_dataframe.fillna(0)
        junc_list = peps_dataframe["NODE"].tolist()

        for i, row in peps_dataframe.iterrows():
            if row["IDEN"] == "JUNC":
                if int(row["NODE"]) == int(junc_list[i-1]):
                    peps_dataframe = peps_dataframe.drop(i)
                elif int(row["NODE"]) == int(junc_list[i-2]):
                    peps_dataframe = peps_dataframe.drop(i)
        
        peps_dataframe = peps_dataframe.reset_index()
        peps_dataframe = peps_dataframe.drop(["index"],axis=1)

        for i, row in peps_dataframe.iterrows():
            if row["IDEN"] == "JUNC":
                peps_dataframe["IDEN"][i+1] = "TANG"

        self.append_log("> Translation job finished...")

        return(peps_dataframe)

    def write_peps(self):
        """Writes output.FRE file, using the translate_to_peps() method."""
        peps_dataframe = self.translate_to_peps_file().copy(deep=True)
        element_index = 0

        self.append_log("> Writing .FRE file...")

        # Fill in CROS cards at the beggining.
        self.append_peps("*----------------------------PROPERTIES\n")
        cros_index = 100

        for item in self.cros_cards:
            self.append_peps("CROS CD=" + str(cros_index) + " OD=" + str(self.ntxt_dataframe["ext diam"].iloc[item]) + " WT=" + str(self.ntxt_dataframe["thick"].iloc[item])+"\n")
            cros_index += 1
        
        self.append_log(">>> " + str(len(self.cros_cards)) + " CROS cards created!")

        # Fill element cards.
        self.append_peps("\n*----------------------------PIPING\n")

        for i, row in peps_dataframe.iterrows():
            if row["IDEN"] != 0:
                self.append_peps(row["IDEN"] + " ")
            if row["NODE"] != 0:
                self.append_peps("PT=" + str(row["NODE"]) + " ")
            if row["DX"] != 0:
                self.append_peps("DX=" + str(row["DX"]) + " ")
            if row["DY"] != 0:
                self.append_peps("DY=" + str(row["DY"]) + " ")
            if row["DZ"] != 0:
                self.append_peps("DZ=" + str(row["DZ"]) + " ")
            if row["RA"] != 0:
                self.append_peps("RA=" + str(row["RA"]) + " ")
            if row["CD"] != 0:
                self.append_peps("CD=" + str(row["CD"]) + " ")
            element_index +=1
            self.append_peps("\n")

        self.append_log(">>> " + str(element_index) + " element cards created!")
        
OriginalText = PepsObj()
OriginalText.write_peps()
