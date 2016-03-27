sudo apt-get update

wget https://bootstrap.pypa.io/get-pip.py && sudo python get-pip.py

sudo apt-get install build-essential autoconf libtool pkg-config python-opengl python-imaging python-pyrex python-pyside.qtopengl idle-python2.7 qt4-dev-tools qt4-designer libqtgui4 libqtcore4 libqt4-xml libqt4-test libqt4-script libqt4-network libqt4-dbus python-qt4 python-qt4-gl libgle3 python-dev

sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose

sudo pip install django gunicorn

sudo apt-get install git

git clone https://github.com/bshurick/w209_project.git
cd w209_project
python manage.py makemigrations surveys
python manage.py migrate

sudo apt-get install nginx
