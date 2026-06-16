import pandas as pd

df=pd.read_csv("../data/sample_of_interest.csv")

for index, row in df.iterrows():
    code=row["Contract"]
    code=(str(code).replace("\ncontract", "\nabstract contract")
          .replace("import \"node_modules/@openzeppelin/contracts/utils/math/SafeMath.sol\"", "import \"openzeppelin/SafeMath.sol\"")
          .replace(";;", ";"). replace("pragma solidity 0.8.0;", "pragma solidity ^0.8.0;")
          .replace("ript\n", ""))
    df.at[index,"Contract"]=code
df.to_csv("sample_of_interest.csv")
