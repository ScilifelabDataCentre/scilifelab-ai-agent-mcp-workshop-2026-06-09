---
name: lipinski
description: Check whether a molecule (given as SMILES) satisfies Lipinski's Rule of Five for oral drug-likeness. Returns MW, LogP, HBD, HBA and a pass/fail flag.
---

# Lipinski's Rule of Five

A small molecule is considered "drug-like" (orally bioavailable) when all four criteria hold:

- Molecular weight ≤ 500 Da
- LogP ≤ 5
- Hydrogen bond donors ≤ 5
- Hydrogen bond acceptors ≤ 10

## Example implementation

```python
from rdkit import Chem
from rdkit.Chem import Descriptors

def lipinski_check(smiles: str) -> dict:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": "Invalid SMILES"}
    mw   = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hbd  = Descriptors.NumHDonors(mol)
    hba  = Descriptors.NumHAcceptors(mol)
    passes = (mw <= 500) and (logp <= 5) and (hbd <= 5) and (hba <= 10)
    return {"MW": mw, "LogP": logp, "HBD": hbd, "HBA": hba, "passes_RO5": passes}
```
