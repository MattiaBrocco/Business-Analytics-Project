import pandas as pd
import numpy as np

class cleaner:
    
    def provs(self, df):
        self.df = df
        # works only if col == "sigla" and df == an13
        col = df["sigla"].values
        l = []
        unmatched_dict = {"FP":["SVIZZERA","DATO MANCANTE","SPAGNA","FRANCIA","GERMANIA",
                                "CHATILLON","BOLZANO/BOZEN","MONTORO INFERIORE","ARGENTINA",
                                "CAGNO","LANZO D'INTELVI","ANTEY-SAINT-ANDRÈ","HONE","RIVIGNANO",
                                "PRÈ-SAINT-DIDIER","NEGRAR","MONTORO SUPERIORE","MONACO","BELGIO",
                                "DUINO-AURISINA","CINA REPUBBLICA POPOLARE","LARI","LU","SAVIGNO",
                                "SANTO STINO DI LIVENZA","FIGLINE VALDARNO","CAPACCIO","PAESI BASSI",
                                "GRESSONEY LA TRINITE'","BREMBILLA","COLBORDOLO","STATI UNITI D'AMERICA",
                                "ROMANIA","LUSSEMBURGO","MESSICO"],
                          "TO":["LEINÌ","VICO CANAVESE","CAMPIGLIONE-FENILE","ALICE SUPERIORE","PECCO"]}
        for x in range(len(col)):
            if type(col[x]) != str:
                if df.loc[x]["comune"] in unmatched_dict["FP"]:
                    l += ["FP"]
                elif df.loc[x]["comune"] in unmatched_dict["TO"]:
                    l += ["TO"]
                else: 
                    l += ["PI"]
            else:
                l += [ col[x] ]
                
        m = []
        for el in l:
            if el in ["AL","AT","BI","CN","NO","VB","VC"]:
                m += ["PI"]
            elif el == "TO":
                m += [el]
            else:
                m += ["FP"]    
        return m
    
    def reduce_agency(self, df):
        # works only if col == "agenzia_tipo" and df == an13
        self.df = df
        col = df["agenzia_tipo"]
        l = []
        for x in col:
            if x in ["PUNTO INFORMATIVO","DATO MANCANTE","PUNTO COMMERCIALE"]: l += ["PUNTO INFORMATIVO/COMMERCIALE/NAN"]
            elif x in ["MUSEO","TEATRI","EDICOLE"]: l += ["MUSEO/TEATRI/EDICOLE"]
            elif x in ["OFFERTA SCUOLE","OFFERTA AZIENDA","GRUPPO D'ACQUISTO"]: l += ["OFFERTE/GRUPPI"]
            elif x == "ACQUISTO ONLINE": l += ["ACQUISTO ONLINE"]
            else: l += ["CRAL/TESSERE ORO/ASSOCIAZIONE"]
        return l
    
    
    def company(self, df):
        """
        This function breaks up the dataset in several parts as the number
        of museums in the original df. Then, since the dataset is ordered by
        the timestamp of the entrance, it is possible to apply the difference
        between each line and the previous one to obtain the timedelta of the
        difference from one entrance to the previous one.
        Finally, just cleanse and fix further the dataset (e.g. create a dichotomous
        and convert it to category).
        """
        self.df = df
        l = df["museo"].unique()
        ldf = [df[df["museo"] == mus] for mus in l]

        for data in ldf:
            if len(data) > 1:
                data.reset_index(drop = True, inplace = True)
                data["min_delta"] = [float(x.total_seconds()/60) for x in data['timestamp'].diff(periods = 1)]
                data["min_delta"][0] = data["min_delta"][1]
            else:
                data["min_delta"] = 0
    
        newdf = pd.concat(ldf)
        newdf.reset_index(inplace = True, drop = True)
    
        less_than_2m = newdf.loc[(newdf["min_delta"] <= 2)]
        more_than_2m = newdf.loc[(newdf["min_delta"] > 2)]
        less_than_2m["min_delta"] = 1
        more_than_2m["min_delta"] = 0
        newdf = pd.concat([less_than_2m, more_than_2m])
        newdf = newdf.sort_index()
        newdf = newdf.rename(columns = {"min_delta":"compagnia"})
    
        return newdf