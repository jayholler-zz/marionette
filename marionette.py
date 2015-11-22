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
    self.directories = {'webroot': '/var/www/html/'}
    self.files = {'index': 'index.php'}
    self.index_content = fixtures.INDEX_DOT_PHP
    self.index_file = ''.join([self.directories['webroot'], self.files['index']])
    self.missing_packages = []

  def check_install_status(self, package):
    print("Checking if {0} is installed".format(package))
    try:
      check_for_package = subprocess.check_call(['/usr/bin/which', package])
      print("Package {0} is verified as installed".format(package))
    except subprocess.CalledProcessError as e:
      print("Package {0} is not installed, adding to missing packages list for installation"
            .format(package))
      self.missing_packages.append(package)

  def install_package(self, package):
    print("Installing {0} automatically".format(package))
    try:
      install_return_code = subprocess.check_call(['/usr/bin/apt-get', '-y','install', package])
    except subprocess.CalledProcessError as e:
      print("Unable to install {0}:\n{1}".format(package, e))

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

  def create_directories():
    for directory in self.directories.values():
      try:
        os.mkdir(directory)
      except IOError as e:
        print("Unable to create required directory {0}".format(directory))

  def check_index_file(self):
    try:
      os.stat(self.index_file)
    except (IOError, OSError) as e:
      print("File not found: {0}".format(self.index_file))
      print("File will be created with configured content")
      self.write_index_dot_php()

  def write_index_dot_php(self):
    try:
      with open(self.index_file, 'w') as f:
        for line in self.index_content:
          f.write(line)
    except IOError as e:
      print("Unable to write {0} due to:\n{1}",format(self.index_file, e))

  def check_index_file_contents(self):
    print("Checking file contents against configuration")
    try:
      os.stat(self.index_file)
      with open(self.index_file, 'r') as f:
          content = f.read()
      if self.index_content == content:
        print("File contents match expected content")
        return True
      else:
        print("File contents DO NOT match expected content")
        print(content)
        return False
    except IOError as e:
      print("Unable to confirm file contents")

  def configure_system(self):
    for package in self.packages:
      self.check_install_status(package)
    for missing_package in self.missing_packages:
      self.install_package(missing_package)
      self.post_install_cleanup(missing_package)
    if not self.check_directories():
      self.create_directories()
    self.check_index_file()
    if self.check_index_file_contents() == False:
      self.write_index_dot_php

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
      except (IOError, subprocess.CalledProcessError) as e:
        print("Failed to restart service {0}".format(service))


if __name__ == "__main__":
  marionette = Marionette()
  marionette.configure_system()
  marionette.restart_services()

