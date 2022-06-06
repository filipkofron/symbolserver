import httpio
from pdb import PDBFile
from pe import PEFile
from fileio import open_rb

def test():
    with open_rb('C:\\Windows\\explorer.exe') as f:
        print(f'C:\\Windows\\explorer.exe: {PEFile(f).hash}')

    with open_rb('c:\\Windows\\ELAMBKUP\\WdBoot.sys') as f:
        print(f'c:\\Windows\\ELAMBKUP\\WdBoot.sys: {PEFile(f).hash}')

    with open_rb('c:\\Windows\\twain_32.dll') as f:
        print(f'c:\\Windows\\twain_32.dll: {PEFile(f).hash}')

    with open_rb('o:\\Apps\\Viveport\\VIVE\\Updater\\App\\ViveCosmosGuide\\ViveCosmosGuide.pdb') as f:
        print(f'o:\\Apps\\Viveport\\VIVE\\Updater\\App\\ViveCosmosGuide\\ViveCosmosGuide.pdb: {PDBFile(f).hash}')

    with httpio.open('http://192.168.2.184/ViveCosmosGuide.exe', 1024 * 1024 * 4) as f:
      print(f'http://192.168.2.184/ViveCosmosGuide.exe: {PEFile(f).hash}')
