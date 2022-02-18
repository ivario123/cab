if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi
echo "============================"
echo "   installing dependecies   "
if [ -f "/etc/arch-release" ]; then
    echo "====   Noticed arch    ====="
    echo "====       Nice        ====="
    echo "==== Installing python3 ===="
    yay -S python38
    echo "============================"
    echo "====  Installing pip3   ===="
    pacman -S python-pip
else
    echo "====  Assuming ubuntu   ===="
    echo "==== Installing python3 ===="
    apt install python3.8
    echo "============================"
    echo "====  Installing pip3   ===="
    apt install python3-pip
fi
echo "============================"
echo "====   Python modules   ===="
pip3 install requests
pip3 install configparser
pip3 install json
pip3 install datetime
pip3 install time
pip3 install discord_webhook
echo "============================"
echo "Done, now all you have to do"
echo "is to run the following command"
echo ""
echo "> python3 cab.py courseid"
echo ""
echo "where courseid is the course you "
echo "want to monitor"
echo "============================"
