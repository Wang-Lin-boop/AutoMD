## AutoMD
Fast to molecular dynamics simulation.  [中文文档](https://zhuanlan.zhihu.com/p/595698129)

- [AutoMD](#automd)
  - [Installtion](#installtion)
      - [1. Install the Desmond package.](#1-install-the-desmond-package)
      - [2. Install the viparr and msys by pip.](#2-install-the-viparr-and-msys-by-pip)
      - [3. Download AutoMD and additional force fields.](#3-download-automd-and-additional-force-fields)
  - [Usage for AutoMD (structures to trajectories)](#usage-for-automd-structures-to-trajectories)
      - [Examples](#examples)
      - [Options](#options)
  - [Molecular Force Fields](#molecular-force-fields)
      - [1. (Recommended) Charmm Small Molecule Library (CSML)](#1-recommended-charmm-small-molecule-library-csml)
      - [2. Amber Lipid, DNA, RNA and others](#2-amber-lipid-dna-rna-and-others)
  - [Usage for AutoTRJ  (trajectory analysis)](#usage-for-autotrj--trajectory-analysis)
      - [Examples](#examples-1)
      - [Options](#options-1)
  - [Disclaimer](#disclaimer)
  - [How to Cite](#how-to-cite)
  - [Acknowledgments](#acknowledgments)


### Installtion
##### 1. Install the Desmond package.  
*   Firstly, download the academic edition of [Desmond package](https://www.deshawresearch.com/resources.html) and install it on you HPC or PC. Of course, you can install the [SCHRODINGER package](https://www.schrodinger.com/downloads/releases) instead the academic edition of Desmond. Then, change the directory to the installtion path of Desmond or SCHRODINGER, and run this command to set the `$Desmond`:  
```
echo "export Desmond=${PWD}/" >> ~/.bashrc
```
*   Then, configure the `${Desmond}/schrodinger.hosts` following this paper: [How do I configure my schrodinger.hosts file for Desmond GPU jobs?
](https://www.schrodinger.com/kb/1844).   
##### 2. Install the viparr and msys by pip.  
*   Firstly, download the msys and viparr.   
```
wget https://github.com/DEShawResearch/viparr/releases/download/4.7.35/viparr-4.7.35-cp38-cp38-manylinux2014_x86_64.whl
wget https://github.com/DEShawResearch/msys/releases/download/1.7.337/msys-1.7.337-cp38-cp38-manylinux2014_x86_64.whl
```
*   Secondly, run these commands to create a new virtual environment for viparr.
```
${Desmond}/run schrodinger_virtualenv.py schrodinger.ve
source schrodinger.ve/bin/activate
pip install --upgrade pip
```
*   Then, install the msys and viparr by Schrödinger pip.
```
pip install msys-1.7.337-cp38-cp38-manylinux2014_x86_64.whl
pip install viparr-4.7.35-cp38-cp38-manylinux2014_x86_64.whl
echo "export viparr=${PWD}/schrodinger.ve/bin" >> ~/.bashrc
```
*   Then, clone the public viparr parameters, and set the environment variable.  
```
git clone https://github.com/DEShawResearch/viparr-ffpublic.git
echo "export VIPARR_FFPATH=${PWD}/viparr-ffpublic/ff" >> ~/.bashrc
```

##### 3. Download AutoMD and additional force fields.
*   Download AutoMD and set the environment variable.
```
git clone https://github.com/Wang-Lin-boop/AutoMD
cd AutoMD
echo "export PATH=${PWD}:\${PATH}" >> ~/.bashrc
chmod +x AutoMD
chmod +x AutoTRJ
source ~/.bashrc
```
*   Copy the mreged Amber force field to `${VIPARR_FFPATH}`.
```
cp -r ff/* ${VIPARR_FFPATH}/
```

### Usage for AutoMD (structures to trajectories)
##### Examples

  1) MD for cytoplasmic protein-ligand complex:  
```
AutoMD -i "*.mae" -S INC -P "chain.name A" -L "res.ptype UNK" -F "S-OPLS"   
```
  1) MD for plasma protein-protein complex:  
```
AutoMD -i "*.mae" -S OUC -F "DES-Amber"  
```
  1) MD for DNA/RNA-protein complex:  
```
AutoMD -i "*.mae" -S "SPC:Cl:0.15-K-Cl+0.02-Mg2-Cl" -F Amber  
```
  1) MD for membrane protein, need to prior place membrane in Meastro.  
```
AutoMD -i "*.mae" -S OUC -l "POPC" -r "Membrane" -F "Charmm"  
```  

##### Options

*   Input parameter: Use Mae or CMS as input, that, MAE can contain pre-defined membrane locations.   
```
  -i    Use a file name (Multiple files are wrapped in "", and split by ' ') "*.mae" or "*.cms" ;  
            or regular expression to represent your input file, default is *.mae.  
```
*   Solution Builder parameter: INC or OUC, this often depends on where the protein is located. 
```
  -S    System Build Mode: <INC>  
        INC: System in cell, salt buffer is 0.15M KCl, water is SPC. Add K to neutralize system.  
        OUC: System out of cell, salt buffer is 0.15M NaCl, water is SPC. Add Na to neutralize system.    
        Custom Instruct: Such as: "TIP4P:Cl:0.15-Na-Cl+0.02-Fe2-Cl+0.02-Mg2-Cl"    
            Interactive addition of salt. Add Cl to neutralize system.  
                for positive_ion: Na, Li, K, Rb, Cs, Fe2, Fe3, Mg2, Ca2, Zn2 are predefined.  
                for nagative_ion: F, Cl, Br, I are predefined.  
                for water: SPC, TIP3P, TIP4P, TIP5P, DMSO, METHANOL are predefined.  
```
*   Membrane builder parameter: Typically, POPC membranes for eukaryotes, whereas POPE membrane for prokaryotes.
```
  -l    Lipid type for membrane box. Use this option will build membrane box. <None>  
            Lipid types: POPC, POPE, DPPC, DMPC.  
```
*   Simulation box builder parameters: box shape and size.
```
  -b    Define a boxshape for your systems. <cubic>  
            box types: dodecahedron_hexagon, cubic, orthorhombic, triclinic  
  -s    Define a boxsize for your systems.  <15.0>  
            for dodecahedron_hexagon and cubic, defulat is 15.0;  
            for orthorhombic or triclinic box, defulat is [15.0 15.0 15.0];  
            If you want use Orthorhombic or Triclinic box, your parameter should be like "15.0 15.0 15.0"  
```
*   Force fields parameters: 
```
  -R    Redistribute the mass of heavy atoms to bonded hydrogen atoms to slow-down high frequency motions.  
  -F    Define a force field to build your systems. <OPLS_2005>  
            OPLS_2005, S-OPLS are recommended to receptor-ligand systems.  
            Amber, Charmm, DES-Amber are recommended to other systems.
            Use the "Custom" to load parameters from input .cms file.  
            
The current force fields support in AutoMD:
    S-OPLS:
        The force fields in Schrödinger packages, recommended to ligand-protein complex.
    OPLS_2005:
        The default force field of Desmond package.
    Amber:
        Recommended to protein, DNA, RNA, lipid and other systems.
        Amber-ff19SB for protein, Amber-ffncaa for non-canonical aa, Amber-ffptm for
        post-translational modifications, amber1jc ion parameters adapt with spce,
        tip3p or tip4pew, Amber-bsc1 for DNA, Amber-tan2018 for RNA.
    Charmm:
        Recommended to protein, DNA, RNA, lipid, carbohydrate and other systems.
        Charmm36m for protein, Charmm36 for carbohydrate, ions, lipid and nucleic acid.
    DES-Amber:
        Recommended to protein-protein complex.
        DES-Amber for protein-protein complex.
```
*   Simulation control parameter:  
```
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

### Molecular Force Fields

_You can retrieve your small molecule in the following database, obtaion the residue name corresponding to your small molecule, and check that this residue name is present in the templates of some kind of force field._    
##### 1. (Recommended) Charmm Small Molecule Library (CSML)    
*   [Charmm-GUI CSML](https://charmm-gui.org/?doc=archive&lib=csml): Small Molecules for Charmm Force fields  

##### 2. Amber Lipid, DNA, RNA and others    
*   [Amber Lipid 17](https://ambermd.org/AmberModels_lipids.php)  
*   [Amber Force Fields for DNA, RNA, and others](https://ambermd.org/AmberModels.php)  
*   [AMBER parameter database](http://amber.manchester.ac.uk/):  Small Molecule parameters for Amber Force fields   

Use the following commands to find the force field which contained your small molecule:   
```
grep ": {$" $VIPARR_FFPATH/*/templates | awk -F: '{print $1,$2}' |  sed 's/\/templates//g' | awk -F/ '{print $NF}' > VIPARR_Dictionary.index
grep '<your residue name>' VIPARR_Dictionary.index
```

_**Then, make sure specify the same ff encompassing this residue in AutoMD when you run the MD simulatuons.**_    
_Note that, in AutoMD, the -F Charmm ff is combined by aa.charmm.c36m, misc.charmm.all36, carb.charmm.c36, ethers.charmm.c35, ions.charmm36, lipid.charmm.c36 and na.charmm.c36, the -F Amber ff is combined by aa.amber.19SBmisc, aa.amber.ffncaa, lipid.amber.lipid17, ions.amber1lm_iod.all, ions.amber2ff99.tip3p, na.amber.bsc1 and na.amber.tan2018, the -F DES-Amber is combined by aa.DES-Amber_pe3.2, dna.DES-Amber_pe3.2, rna.DES-Amber_pe3.2 and other force fields in -F Amber._   

_Alternatively, you can also refer to the method [here for Amber](https://www.protocols.io/view/how-to-assign-amber-parameters-to-desmond-generate-bp2l6bqwkgqe/v1?step=5) or [here for Charmm](https://www.protocols.io/view/how-to-assign-charmm-parameters-to-desmond-generat-q26g78pr8lwz/v1?step=4) using self prepared Amber or Charmm small molecule force field files._   

### Usage for AutoTRJ  (trajectory analysis)

_In order to facilitate the analysis of Desmond MD trajectories, we have developed a script named AutoTRJ, which collects all common analysis functions and implements them into a customizable analysis pipeline.   

##### Examples

  1) Analysis for protein-ligand complex:   
```
AutoTRJ -i "*-md" -J PL_Analysis -M "APCluster_5+LigandAPCluster_5+LigandCHCluster_5_1.0+MMGBSA+FEL" -L "ligand" -t "1:1001:10" -C "not sovent" 
```
  2) Analysis for small molecular probes distribution on the protein surface:  
```
AutoTRJ -i "*-md" -J Distribution -M "APCluster_5+Occupancy+FEL" -C "not sovent" -L "res.ptype UNK"
```
  3) Analysis for protein-protein interaction: 
```
AutoTRJ -i "*-md" -J PPI -M "APCluster_5+PPIContact+FEL" -C "not sovent" -L "chain.name A"
```

##### Options

Typically, when running MD simulations, we use at least three random seeds and perform three different simulation replicas. During the analysis stage, we can merge the trajectories using wildcards, such as `*-md`, and input them into the analysis pipeline._  

```
  -i <string>   The path to trajectory or regular expression for trajectories(will be merged). such as "*-md".
  -J <string>   Specify a basic jobname for this task, the basename of -i is recommended.
```

_The analysis pipeline for a task is specified using the -M parameter. For example, you can set up an analysis pipeline by using the following command: `-M "APCluster_5+PPIContact+MMGBSA"`. This pipeline will first perform unsupervised clustering of the trajectory using the affinity propagation clustering algorithm and output the structures of the top five clusters. Then, it will analyze the interactions on the protein-protein interface (PPI). Finally, it will analyze the MMGBSA binding free energy between the specified two components._    

```
  -M <string>   The running mode for this analysis task. the <..> means some options.
                APCluster_<n>: affinity propagation clustering, the <n> is the number of most populated clusters.
                CHCluster_<n>_<cutoff>: centroid hierarchical clustering, the <cutoff> is the RMSD thethreshold.
                LigandAPCluster_<n>: APCluster for ligand, require "-L" option.
                LigandCHCluster_<n>_<cutoff>: CHCluster for ligand, require "-L" option.
                Occupancy: calculates the occupancy of component 2 in trajectory, require "-L" option.
                PPIContact: identifies interactions occurring between the components, require "-L" option.
                FEL: analyze the free energy landscape (FEL) for CA atoms, and cluster the trajectories by FEL.
                CCM: plot the cross-correlation matrix of the trajectory.
                SiteMap_<n>: running SiteMap on all frames of the trajectory, the <n> is the number of sites.
                PocketMonitor: monitor the ligand binding pocket n the trajectory, require "-L" option.
                MMGBSA: run MM-GBSA on the trajectory, require "-L" option.
                BFactor: calculate atom B-factors from trajectory (receptor and ligand).
                RMSF: calculate RMSF from trajectory (receptor).
                DistanceMonitor_<res1_asl>_<res2_asl>_<mode>:
                    monitor the distance between two residues in the trajectory,
                    the mode can be min or center for minimum distance or center of mass distance.
                AngleMonitor_<atom1_num>_<atom2_num>_<atom3_num>:
                    monitor the angle between three atoms in the trajectory.
                DihedralMonitor_<atom1_num>_<atom2_num>_<atom3_num>_<atom4_num>:
                    monitor the dihedral angle between four atoms in the trajectory.
                HbondMonitor_<ASL1>_<ASL2>:
                    monitor the hydrogen bond between two ASLs in the trajectory.
                CustomFEL_<mode>:
                    analyze the free energy landscape (FEL),the mode can be PCA, "RMSD:ASL1_RG:ASL2","RMSD:ASL1_DIS:ASL2,ASL3_dismode",
                    "RG:ASL1_DIS:ASL2,ASL3_dismode", "DIS:ASL1,ASL2_DIS:ASL3,ASL4_dismode", "RMSD:ASL1_RMSD:ASL2"
                ConvertXTC: convert the trajectory to XTC format.
            You can parallel the analysis task by "+", such as, "APCluster_5+PPIContact+MMGBSA".
```

_Note that you need to split the analysis tasks using the plus sign `+`._

_To specify the two components of the protein-protein interface (PPI), or even a small molecule and a protein, you can use the -R and -L parameters. The -R parameter is used to specify the receptor component, while the -L parameter is used to specify the ligand component. By providing the appropriate input for these parameters, you can accurately define the two components involved in the interaction analysis._    

_Before executing the analysis pipeline, additional preprocessing steps can be applied to the trajectories, such as extracting a subset of the trajectories._   

```
Trajectories Processing Options:
  -T <string>   Slice trajectories when analyzed, if more than one trajectories given by -i, this slice will applied to all of them. The default is None. Such as "100:1000:1". <START:END:STEP>
```

_In addition to the preprocessing steps before analysis, the script also provides the functionality to consider only a subset of trajectories during the MM-GBSA calculations. This is mainly due to the computational complexity of MM-GBSA compared to other analysis tasks. Therefore, it is common practice to reduce the number of frames used for MM-GBSA calculations, for example, by computing MM-GBSA every 10 steps._   

```
  -t <string>   Slice trajectories when calculating MM/GBSA, such as "100:1000:10". <START:END:STEP>
```

_In the MM-GBSA calculations, if you have pre-defined membrane position parameters for the membrane protein (which can be set in any panel of the Prime module during Desmond system setup), it is possible to replace the explicit membrane in the system with an implicit membrane during the MM-GBSA computation._    

```
  -m            Treat the explicit membrane to implicit membrane during MM-GBSA calculation.
```

_Sometimes, it is desirable not only to obtain representative conformations for each cluster generated by clustering analysis but also to extract all conformations within each cluster to create a conformational ensemble for reaction local free energy landscape. For this purpose, the `-c` parameter can be used to modify the output from representative conformations of clustering to output a representative trajectory._   

```
  -c            During the clustering process, the frames of a trajectory are preserved for each cluster, while representative members are stored in the CMS files.
```

_By default, trajectories are centered around the solute's center of mass using the first frame to ensure accuracy during analysis. However, for certain specific tasks, such as Occupancy, mere centering is insufficient. Often, it is necessary to superimpose the conformations in the trajectory onto a representative initial or experimental structure. This functionality can be achieved using the `-A` or `-a` options. The `-A` option allows specifying a reference structure, while the `-a` option aligns the first frame of the trajectory to serve as the reference structure._    

```
  -A <file>     Align the trajectory to a reference structure, given in ".mae" format.
  -a            Align the trajectory to the frist frame.
```

_In analytical analysis, the removal of solvents may greatly accelerates the speed of analysis. This option is achieved through -C or -P. The -C option allows the direct use of ASL expressions to remove a portion of the system, while -P evaporates the water in the solvent box, retaining only the surface water of the solute._   

```
  -C <ASL>      Set a ASL to clean the subsystem from trajectory, such as -C "not solvent".
  -P            Parch waters far away from the component 2.
  -w <int>      Number of retained water molecules for parch (-P) stage. <200>
```

### Disclaimer

_This script was developed to speed up my own work, and I put this script here for convenience for sharing to some people who need it. Discussion with me is welcome if you also wish to use it and have some problems, but I do not guarantee that we will solve it. Of note, this script was developed based on a series of software from the [D. E. Shaw Research](https://github.com/DEShawResearch), all credit to D. E. Shaw Research. I declare no competing interest._    

### How to Cite

We first used AutoMD in this work below, and if you would like to cite AutoMD, please cite the paper below.   

A new variant of the colistin resistance gene MCR-1 with co-resistance to β-lactam antibiotics reveals a potential novel antimicrobial peptide. Liang L, Zhong LL, Wang L, Zhou D, Li Y, et al. (2023) A new variant of the colistin resistance gene MCR-1 with co-resistance to β-lactam antibiotics reveals a potential novel antimicrobial peptide. _PLOS Biology_ 21(12): e3002433. https://doi.org/10.1371/journal.pbio.3002433


### Acknowledgments

We would like to express our special thanks to the following individuals and organizations, whose contributions have been invaluable to our research:    
*   Thilo Mast and Dmitry Lupyan for sharing their methods for using alternative force fields in Desmond, which provided us with a valuable foundation for our work    
*   D E Shaw Research and Schrödinger for their significant contributions to the development and maintenance of the Desmond software, which has allowed us to leverage this powerful platform for our research   
*   Charlie for his/her scprit for FEL plots which can be found at [here](https://github.com/CharlesHahn/DuIvy/tree/master/sources)
