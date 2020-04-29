#!/bin/sh
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt -y install git

if ! type jupyter  > /dev/null; then
  echo "" >> /root/.bashrc
  echo "# Adding anaconda3 path to PATH" >> /root/.bashrc
  echo "export PATH=/opt/anaconda3/bin:$PATH" >> /root/.bashrc
  echo "Anaconda3 installation has been started!"
  echo "Getting http://repo.continuum.io/archive/Anaconda3-2019.10-Linux-x86_64.sh"
  wget http://repo.continuum.io/archive/Anaconda3-2019.10-Linux-x86_64.sh
  echo "Running Anaconda3-2019.10-Linux-x86_64.sh"
  ann_path=/opt/anaconda3
  echo "Anaconda3 path is $ann_path"
  bash Anaconda3-2019.10-Linux-x86_64.sh -b -p $ann_path
  rm Anaconda3-2019.10-Linux-x86_64.sh
  export PATH=/opt/anaconda3/bin:$PATH
fi

# Install few important libraries
conda install -y -c anaconda pandas
conda install -y -c anaconda numpy
conda install -y -c anaconda scikit-learn
conda install -y -c conda-forge tensorflow
conda install -y -c conda-forge keras
conda install -y -c pytorch pytorch
conda install -y -c conda-forge google-cloud-storage
conda install -y -c conda-forge google-cloud-bigquery
conda install -y -c conda-forge google-cloud-sdk
conda install -y -c conda-forge google-cloud-core
conda install -y -c conda-forge gcsfs
conda install -y -c plotly plotly
conda install -y pip
conda install -y -c conda-forge pyspark



for i in $(awk -F: '($3>=1000)&&($1!="nobody"){print $1}' /etc/passwd); do
  echo "Updating users specific setups, for user $i"
  bashrc="/home/$i/.bashrc"
  echo "Updating $bashrc"
  echo "" >> $bashrc
  echo "# Adding anaconda3 path to PATH" >> $bashrc
  echo "export PATH=/opt/anaconda3/bin:$PATH" >> $bashrc

done

echo "All is done!!!"
exec bash
