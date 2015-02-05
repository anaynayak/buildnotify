# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.box_check_update = false

  config.vm.provider "virtualbox" do |vb|
    vb.gui = true
    vb.memory = "1024"
  end

  config.vm.provision "shell", inline: <<-SHELL
     sudo apt-get update
     sudo apt-get install -y ubuntu-desktop xinit unity
     sudo apt-get install -y python-qt4 qt4-dev-tools python-tz python-dateutil pyqt4-dev-tools python-support python-pip
     sudo pip install paver
  SHELL
end
