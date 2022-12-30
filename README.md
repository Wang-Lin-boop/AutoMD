# AutoMD
Fast to molecular dynamics simulation. 

Installtion
==== 
### 1. Install the Desmond package.  

Firstly, download the academic edition of [Desmond package](https://www.deshawresearch.com/resources.html) and install it on you HPC or PC. Of course, you can install the [SCHRODINGER package](https://www.schrodinger.com/downloads/releases) instead the academic edition of Desmond. Then, set the environment variable `$Desmond` to the installtion path of Desmond.  e.g. ```export Desmond=/public/home/wanglin3/software/DS21```.   

You can change the path to the installtion path of Desmond or SCHRODINGER, and run this command:  
```
echo "export Desmond=${PWD}/" >> ~/.bashrc
```

### 2. Install the viparr and msys by pip.  

Firstly, download the msys and viparr.   
```
wget https://github.com/DEShawResearch/viparr/releases/download/4.7.35/viparr-4.7.35-cp38-cp38-manylinux2014_x86_64.whl
wget https://github.com/DEShawResearch/msys/releases/download/1.7.337/msys-1.7.337-cp38-cp38-manylinux2014_x86_64.whl
```
Secondly, run these commands to create a new virtual environment for viparr.
```
${Desmond}/run schrodinger_virtualenv.py schrodinger.ve
source schrodinger.ve/bin/activate
pip install --upgrade pip
```
Then, install the msys and viparr by Schrödinger pip.
```
pip install msys-1.7.337-cp38-cp38-manylinux2014_x86_64.whl
pip install viparr-4.7.35-cp38-cp38-manylinux2014_x86_64.whl
echo "export viparr=${PWD}/schrodinger.ve/bin" >> ~/.bashrc
```

### 3. Download the force field library for Viparr.  

Then, clone the public Viparr parameters from D.E. Shaw Research's GitHub repository, and set the environment variable. 
```
git clone git://github.com/DEShawResearch/viparr-ffpublic.git
echo "export VIPARR_FFPATH=${PWD}/viparr-ffpublic/ff" >> ~/.bashrc
```

### 4. Download AutoMD and set environment variable.

```
git clone https://github.com/Wang-Lin-boop/AutoMD
cd AutoMD
echo "alias AutoMD=${PWD}/AutoMD" >> ~/.bashrc
chmod +x AutoMD
source ~/.bashrc
```
Copy the mreged Amber force field to `${VIPARR_FFPATH}`.
```
cp -r ff/* ${VIPARR_FFPATH}/
```

Usage
====
__Options:__  
```
Input parameter:  
  -i    Use a file name (Multiple files are wrapped in "", and split by ' ') "*.mae" or "*.cms" ;  
            or regular expression to represent your input file, default is *.mae.  

System Builder parameter:  
  -S    System Build Mode: <INC>  
        INC: System in cell, salt buffer is 0.15M KCl, water is SPC. Add K to neutralize system.  
        OUC: System out of cell, salt buffer is 0.15M NaCl, water is SPC. Add Na to neutralize system.    
        Custom Instruct: Such as: "TIP4P:Cl:0.15-Na-Cl+0.02-Fe2-Cl+0.02-Mg2-Cl"    
            Interactive addition of salt. Add Cl to neutralize system.  
                for positive_ion: Na, Li, K, Rb, Cs, Fe2, Fe3, Mg2, Ca2, Zn2 are predefined.  
                for nagative_ion: F, Cl, Br, I are predefined.  
                for water: SPC, TIP3P, TIP4P, TIP5P, DMSO, METHANOL are predefined.  
  -l    Lipid type for membrane box. Use this option will build membrane box. <None>  
            Lipid types: POPC, POPE, DPPC, DMPC.  
  -b    Define a boxshape for your systems. <cubic>  
            box types: dodecahedron_hexagon, cubic, orthorhombic, triclinic  
  -s    Define a boxsize for your systems.  <15.0>  
            for dodecahedron_hexagon and cubic, defulat is 15.0;  
            for orthorhombic or triclinic box, defulat is [15.0 15.0 15.0];  
            If you want use Orthorhombic or Triclinic box, your parameter should be like "15.0 15.0 15.0"  
  -R    Redistribute the mass of heavy atoms to bonded hydrogen atoms to slow-down high frequency motions.  
  -F    Define a force field to build your systems. <OPLS_2005>  
            OPLS_2005, S-OPLS are recommended to receptor-ligand systems.  
            Amber, Charmm, DES-Amber are recommended to other systems. Use -O to show more details.  
            Use the "Custom" to load parameters from input .cms file.  

Simulation control parameter:  
  -m    Enter the maximum simulation time for the Brownian motion simulation, in ps. <100>  
  -r    The relaxation protocol before MD, "Membrane" or "Solute". <Solute>  
  -e    The ensemble class in MD stage, "NPT", "NVT", "NPgT". <NPT>  
  -t    Enter the Molecular dynamics simulation time for the product simulation, in ns. <100>  
  -T    Specify the temperature to be used, in kelvin. <310>  
  -N    Number of Repeat simulation with different random numbers. <1>  
  -P    Define a ASL to receptor, such as "protein".  
  -L    Define a ASL to ligand and run interaction analysis, such as "res.ptype UNK".  
  -u    Turn off md simulation, only system build.  
  -C    Set constraint to an ASL, such as "chain.name A AND backbone"  
  -f    Set constraint force, default is 10.  
  -o    Specify the approximate number of frames in the trajectory.  <1000>  
        This value is coupled with the recording interval for the trajectory and the simulation time:  
        the number of frames times the trajectory recording interval is the total simulation time.  
        If you adjust the number of frames, the recording interval will be modified.  
```
__Example:__   
```
1) MD for cytoplasmic protein-ligand complex:  
AutoMD -i "*.mae" -S INC -P "chain.name A" -L "res.ptype UNK" -F "OPLS_2005"  
2) MD for plasma protein-protein complex:  
AutoMD -i "*.mae" -S OUC -F "DES-Amber"  
3) MD for DNA/RNA-protein complex:  
AutoMD -i "*.mae" -S "SPC:Cl:0.15-K-Cl+0.02-Mg2-Cl" -F Amber  
4) MD for membrane protein, need to prior place membrane in Meastro.  
AutoMD -i "*.mae" -S OUC -l "POPC" -r "Membrane" -F "Charmm"  
```  

Disclaimer
====
_This script was developed to speed up my own work, and I put this script here for convenience for sharing to some people who need it. Discussion with me is welcome if you also wish to use it and have some problems, but I do not guarantee that you will solve it. Of note, this script was developed based on a series of software from the [D. E. Shaw Research](https://github.com/DEShawResearch), this repository declare no competing interest._    

