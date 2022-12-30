# AutoMD
Fast to molecular dynamics simulation. 

Installtion
==== 
### 1. Install the Desmond academic edition.  

Firstly, download the linux version of [Desmond package](https://www.deshawresearch.com/resources.html) and install it on you HPC or PC.   
Of course, you can install the [SCHRODINGER package](https://www.schrodinger.com/downloads/releases) instead the academic edition of Desmond.   
Then, set the environment variable `$Desmond` to the installtion path of Desmond.  e.g. ```export Desmond=/public/home/wanglin3/software/DS21```
You can change the path to the installtion path of Desmond or SCHRODINGER, and run this command:  
```
echo "export Desmond=${PWD}/" >> ~/.bashrc
```

### 2. Install the Viparr by pip.  

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

Usage
====


Disclaimer
====
This script was developed to speed up my own work, and I put this script here for convenience for sharing to some people who need it. Discussion with me is welcome if you also wish to use it and have some problems, but I do not guarantee that you will solve it. Of note, this script was developed based on a series of software from the [D. E. Shaw Research](https://github.com/DEShawResearch), this repository declare no competing interest.     

