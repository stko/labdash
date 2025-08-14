# this script does the bare operations to get the installation files in place
# to run it from the command line, use:
# bash <(curl -s http://mywebsite.com:8080/bootstrap.sh)
echo "Lapdash tries to install git to clone the repository to disk"
echo update packages
sudo apt-get update --assume-yes
## install some basic packages
sudo apt-get install --assume-yes \
git \
python3-venv \
python3-pip \
python3-setuptools \
python3-wheel \
python3-dev \
python3

cd
# git clone --depth 1 https://github.com/stko/labdash.git
## the development workaround
wget  http://192.168.1.185:8000/development.zip -O development.zip && unzip development.zip
if [ ! -f development.zip ]; then
	echo "development.zip not found! - Exiting.."
	exit 1 
fi
# do the software setup
cd ~/labdash
python3 -m venv .venv
source .venv/bin/activate
pip install .
chmod +x *.sh
# do the hardware setup
cd raspi
chmod +x *.sh
./raspi_install.sh
# 
