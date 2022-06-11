from typing import Optional
from pdb import PDBFile
from pe import PEFile

def hash(file) -> Optional[str]:
  try:
    return PEFile(file).hash
  except:
    pass

  try:
    return PDBFile(file).hash
  except:
    pass

  return None
