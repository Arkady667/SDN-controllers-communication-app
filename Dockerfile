FROM ubuntu:trusty-20171207

RUN apt-get update && apt-get -y install sudo
RUN apt-get -y install openssl
RUN apt-get -y install libcap-ng-dev
RUN apt-get -y install apt-utils
RUN apt-get -y install net-tools
RUN apt-get install -y iputils-ping
RUN apt-get install git -y
RUN apt-get install curl -y && apt-get install wget -y

#JAVA-install
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y  software-properties-common && \
    add-apt-repository ppa:webupd8team/java -y && \
    apt-get update && \
    apt-get clean
COPY jdk8 /opt/jdk8
RUN cd opt && ls
RUN update-alternatives --install /usr/bin/java java /opt/jdk8/jdk1.8.0_161/bin/java 100 && \
	update-alternatives --install /usr/bin/javac javac /opt/jdk8/jdk1.8.0_161/bin/javac 100 && \
	update-alternatives --display java && \
	update-alternatives --display javac && \
	java -version


#Mininet-install
COPY mininet /root/mininet
RUN cd /root/mininet && util/install.sh -nf

#OVS-install
COPY openvswitch-2.7.1 /root/openvswitch-2.7.1
RUN cd /root/openvswitch-2.7.1 && ./configure && make && make install
ENV PATH=$PATH:/usr/local/share/openvswitch/scripts

# OpenDayLight
#COPY odl /home/student/odl

# Ryu
RUN add-apt-repository ppa:jonathonf/python-3.6 && \
	apt-get update -y && \
	apt-get install python3.6 -y && \
	apt-get install gcc python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev zlib1g-dev -y
RUN apt-get install python-pip -y && pip install ryu 

#Eclipse-install
COPY eclipse /home/student/eclipse


#Add student user
RUN adduser --disabled-password --gecos '' student
RUN echo student:student | chpasswd
RUN usermod -a -G sudo student
RUN echo "student ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/student && chmod 0440 /etc/sudoers.d/student
RUN cp /etc/skel/.bashrc /home/student & cp /etc/skel/.profile /home/student

#Add symlink to start eclipse
RUN ln -s /home/student/eclipse/eclipse /usr/bin/eclipse

#PyCharm
COPY pycharm /home/student/pycharm

# Java fix
RUN apt-cache search java | grep openjdk && apt-get install openjdk-7-jdk -y && echo $JAVA_HOME

#Floodlight
COPY floodlight /home/student/floodlight
RUN apt-get install -y build-essential maven
RUN mkdir /var/lib/floodlight
RUN chmod 777 /var/lib/floodlight
RUN cd /home/student/floodlight 

#Apache2 install
RUN apt-get -y install apache2

#Floodlight WEB-GUI
#RUN rm /var/www/html/index.html
#COPY floodlight-webui/ /var/www/html/

#Change persmissions for eclipse and floodlight
RUN cd /home/student && chown -R student .
RUN cd /home/student && chgrp -R student .

#Wireshark-install
RUN DEBIAN_FRONTEND=noninteractive apt-get install wireshark -y
RUN groupadd wireshark && usermod -a -G wireshark student && chgrp wireshark /usr/bin/dumpcap && chmod 750 /usr/bin/dumpcap && setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap

#Install text editors
RUN apt-get install gedit nano -y

#SET X11UseLocalhost=no
RUN echo 'X11UseLocalhost=no' >> /etc/ssh/sshd_config

#SET Xauthority for root user for correct authentication for X11 forwarding
RUN echo 'export XAUTHORITY=/home/student/.Xauthority' >> /etc/profile 

#Install CURL
RUN apt-get install -y curl

#RUN sshd and start OVS 
CMD service ssh start && service apache2 start && ovs-ctl start && bash

#JAVA fix
RUN update-alternatives --set java /opt/jdk8/jdk1.8.0_161/bin/java

# Verification
RUN pip -V
RUN pip install --ignore-installed six
