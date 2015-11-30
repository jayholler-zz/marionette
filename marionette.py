#!/usr/bin/python2.7

from __future__ import print_function

import os
import subprocess

import fixtures

class Marionette(object):
  """A very simple object for configuring Ubuntu systems as specified by parameters in __init__"""

  def __init__(self):
    self.packages = ['apache2', 'php5']
    self.services = ['apache2']
    self.directories = {'webroot': '/var/www/html/', 'etc': '/etc/'}
    self.files = {
      'index': ''.join(self.directories['webroot'], 'index.php'),
      'resolv': ''.join(self.directories['etc'], 'resolv.conf')
    }
    self.index_content = fixtures.INDEX_DOT_PHP
    self.resolvconf_content = fixtures.RESOLV_CONF
    self.file_contents = {'index': self.index_content, 'resolv': self.resolvconf_content}

    self.missing_packages = []

  def check_install_status(self, package):
    print("Checking if {0} is installed".format(package))
    try:
      subprocess.check_call(['/usr/bin/which', package])
      print("Package {0} is verified as installed".format(package))
    except subprocess.CalledProcessError as e:
      print("Package {0} is not installed, adding to missing packages list for installation"
            .format(package))
      print("Failure received was: {0}".format(e))
      self.missing_packages.append(package)

  def install_package(self, package):
    print("Installing {0} automatically".format(package))
    try:
      return_code = subprocess.check_call(['/usr/bin/apt-get', '-y','install', package])
    except subprocess.CalledProcessError as e:
      print("Unable to install {0} due to:\n{1}\n return code: {2}".format(package, e, return_code))

  def post_install_cleanup(self, package):
    print("Doing post install cleanup for package {0}".format(package))
    if package == 'apache2':
      if os.path.isfile('/var/www/html/index.html'):
        os.rename('/var/www/html/index.html', '/var/www/html/index.apache2_default')

  def check_directories(self):
    print("Checking for existence of provided directories")
    for directory in self.directories.values():
      print("Checking for directory: {0}".format(directory))
      try:
        os.stat(directory)
        return True
      except OSError:
        return False

  def create_directories(self):
    for directory in self.directories.values():
      try:
        os.mkdir(directory)
      except IOError as e:
        print("Unable to create required directory {0} due to:\n{1}".format(directory, e))

  def check_files(self):
    for name, cfg_file in self.files.items():
      try:
        os.stat(cfg_file)
      except (IOError, OSError):
        print("File not found: {0}".format(cfg_file))
        print("File will be created with configured content")
        self.write_config_file(name, cfg_file)

  def write_config_file(self, name, cfg_file):
    if name == 'resolv':
      print("Using resolvconf -u to update /etc/resolv.conf")
      try:
        subprocess.check_call(['/sbin/resolvconf', '-u'])
        return
      except subprocess.CalledProcessError as e:
        print("Unable to run resolvconf to update /etc/resolv.conf")
        print("Writing /etc/resolv.conf directly from provided expected contents")
    try:
      with open(cfg_file, 'w') as f:
        for line in self.file_contents[name]:
          f.write(line)
    except IOError as e:
      print("Unable to write {0} due to:\n{1}",format(cfg_file, e))

  def check_file_contents(self, name, cfg_file):
    print("Checking file contents against configuration")
    try:
      os.stat(cfg_file)
      with open(cfg_file, 'r') as f:
          content = f.read()
      if self.file_contents[name] == content:
        print("File contents match expected content")
        return True
      else:
        print("File contents DO NOT match expected content")
        print(content)
        return False
    except IOError:
      print("Unable to confirm file contents")

  def configure_system(self):
    for package in self.packages:
      self.check_install_status(package)
    for missing_package in self.missing_packages:
      self.install_package(missing_package)
      self.post_install_cleanup(missing_package)
    if not self.check_directories():
      self.create_directories()
    self.check_files()
    for name, cfg_file in self.files.items():
      if self.check_file_contents(name, cfg_file) == False:
        self.write_config_file(name, cfg_file)

  def restart_services(self):
    for service in self.services:
      try:
        print("Checking that service {0} is running".format(service))
        check = subprocess.call(['/usr/sbin/service', service, 'status'])
        if check == 0:
          print("Restarting service {0}".format(service))
          subprocess.check_call(['/usr/sbin/service', service, 'restart'])
        else:
          print("Service {0} wasn't running, attempting to start now".format(service))
          subprocess.check_call(['/usr/sbin/service', service, 'start'])
      except (IOError, subprocess.CalledProcessError):
        print("Failed to restart service {0}".format(service))


if __name__ == "__main__":
  marionette = Marionette()
  marionette.configure_system()
  marionette.restart_services()


