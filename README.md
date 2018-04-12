# plivo-fs-assignment

**Problem Statement**
* Freeswitch Installation
* Freeswitch as SIP Registrar (accept both SIP UDP and SIP TCP connections)
* Any other SIP call or SIP registration should be rejected if other than default Users (1000,1001)
* Using event_socket module implement REST API to make outbound call on default SIP user

**SSH to AWS debain instance**

 Change permission of `fs-plivo.pem` file
 
    chmod 400 plivo-fs.pem 
 
 Login in to server using user `admin`
 
    ssh -i plivo-fs.pem admin@52.221.185.109
 
 Become `root` and update source and package
 
    sudo su
    apt-get update && apt-get dist-update 
	
**Build & Install FreeSWITCH**
 -
 First update your Debian box & install curl & git.
 
    apt-get update && apt-get install -y curl git
 
 Add FreeSWITCH GPG key to APT sources keyring.
 
    curl https://files.freeswitch.org/repo/deb/debian/freeswitch_archive_g0.pub | apt-key add -
 
 Add FreeSWITCH repository to APT sources.
 
    echo "deb http://files.freeswitch.org/repo/deb/freeswitch-1.6/ jessie main" > /etc/apt/sources.list.d/freeswitch.list
 
 Update once again 
 
    apt-get update
 
 Now lets first install FreeSWITCH dependencies.
 
    apt-get install -y --force-yes freeswitch-video-deps-most 
 
 Few package still remains required to compile like `mod_fsv`, so install them as
 
    apt-get install -y libyuv-dev libvpx2-dev
 
 Grab source code of FreeSWITCH as follows
 
    git config --global pull.rebase true
    cd /usr/src/
    git clone https://freeswitch.org/stash/scm/fs/freeswitch.git freeswitch.git
 
 Now lets compile FreeSWITCH source for version 1.6
 
    cd freeswitch.git
    git checkout v1.6
    ./bootstrap.sh -j
    ./configure -C
    make && make install
 
 Now lets compile sounds
 
 
    make all cd-sounds-install cd-moh-install
 
 Lets create simlinks to required binaries to access them from anywhere
  
    ln -s /usr/local/freeswitch/bin/freeswitch /usr/bin/freeswitch
    ln -s /usr/local/freeswitch/bin/fs_cli /usr/bin/fs_cli

**Set Owner & Permissions**

    cd /usr/local
    groupadd freeswitch
    adduser --disabled-password  --quiet --system --home /usr/local/freeswitch --gecos "FreeSWITCH Voice Platform" --ingroup freeswitch freeswitch
    chown -R freeswitch:freeswitch /usr/local/freeswitch/
    chmod -R ug=rwX,o= /usr/local/freeswitch/
    chmod -R u=rwx,g=rx /usr/local/freeswitch/bin/

**Starting FreeSWITCH service on boot automatically**
 
    cp freeswitch.service /lib/systemd/system/freeswitch.service

 Now execute following commands in your shell
 
    chmod 750 /lib/systemd/system/freeswitch.service
    ln -s /lib/systemd/system/freeswitch.service /etc/systemd/system/freeswitch.service
    systemctl daemon-reload
    systemctl enable freeswitch.service

**Start FreeSWITCH**
 
    systemctl start freeswitch.service
    fs_cli
    
**Firewall Configuration in AWS Security Group**

Open UDP ports
  * SIP -> 5060
  * RTP -> 16384-32768
  
Open TCP Ports
  * SIP -> 5060
  * ESL -> 8081-8082
  * HTTP -> 80
  * HTTPS ->443

**Freeswitch Configuration**

External SIP IP Configuration
> Edit conf/vanilla/vars.xml

	<X-PRE-PROCESS cmd="exec-set" data="bind_server_ip=curl -s http://instance-data/latest/meta-data/public-ipv4"/>
	<X-PRE-PROCESS cmd="exec-set" data="external_rtp_ip=curl -s http://instance-data/latest/meta-data/public-ipv4"/>
	<X-PRE-PROCESS cmd="exec-set" data="external_sip_ip=curl -s http://instance-data/latest/meta-data/public-ipv4"/>

Enable RTP ports
> Edit /usr/local/freeswitch/conf/autoload_configs/switch.conf.xml

	<param name="rtp-start-port" value="16384"/>
	<param name="rtp-end-port" value="32768"/>
	
	
**Enable 'mod_shout' for playing mp3 and remote audio**

Install Depedencies 

	apt-get install libvorbis0a libogg0 libogg-dev libvorbis-dev

> In modules.conf (source) append line
	
	formats/mod_sndfile
	formats/mod_shout    <--- NEW

Configure/Make:

	./configure && make install

Enable `mod_shout`
 > Add in /usr/local/freeswitch/conf/autoload_configs/modules.conf.xml mod_shout to the list	

	<load module="mod_shout"/>  

 > Modify the priority of CODEC in /usr/local/freeswitch/conf/vars.xml

	<X-PRE-PROCESS cmd="set" data="global_codec_prefs=PCMU"/>
	<X-PRE-PROCESS cmd="set" data="outbound_codec_prefs=PCMU"/>
	
**REST API IMPLEMENTATION**

* Install PIP

		apt-get install python-pip

* Install virtualenwrapper
 
 		pip install virtualenvwrapper

* Append in .bashrc to enable virtualenv package
	
		export WORKON_HOME=$HOME/.virtualenvs
		export MSYS_HOME=/c/msys/1.0
		source /usr/local/bin/virtualenvwrapper.sh

* create virtual env

		mkvirtualenv plivo-fs

* enable mod_python in freeswitch

		make pymod
		make pymod-install

* install PIP Dependencies 

> All the dependencies are in rest_service/requirements.txt

		pip install -r rest_service/requirements


**References**

* Freeswitch Installation :
[http://howto.lintel.in/how-to-install-freeswitch-1-6-on-debian-8-jessie/](http://howto.lintel.in/how-to-install-freeswitch-1-6-on-debian-8-jessie/)

* Firewall setting and  External IP Config in freeswitch :
[https://freeswitch.org/confluence/display/FREESWITCH/Amazon+EC2](https://freeswitch.org/confluence/display/FREESWITCH/Amazon+EC2)

* Python ESL : [https://freeswitch.org/confluence/display/FREESWITCH/Python+ESL](https://freeswitch.org/confluence/display/FREESWITCH/Python+ESL)


