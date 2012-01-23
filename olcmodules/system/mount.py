#!/usr/bin/env python
##############################################################################
#    OpenLFConnect
#
#    Copyright (c) 2012 Jason Pruitt <jrspruitt@gmail.com>
#
#    This file is part of OpenLFConnect.
#    OpenLFConnect is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OpenLFConnect is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with OpenLFConnect.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################



##############################################################################
# Title:   OpenLFConnect
# Version: Version 0.4
# Author:  Jason Pruitt
# Email:   jrspruitt@gmail.com
# IRC:     #didj irc.freenode.org
# Wiki:    http://elinux.org/LeapFrog_Pollux_Platform
##############################################################################

import os
import sys
from time import sleep
from subprocess import Popen, PIPE

class connection(object):
    def __init__(self, device_id='', mount_point='', debug=False):
        self.debug = debug
        self._type = 'mount'
        self._linux_dev = '/dev/leapfrog'
        self._vendor_name = 'leapfrog'
        
        self._device_id = device_id
        self._mount_point = mount_point
        
        self._time_out = 30

        if sys.platform == 'win32':
            self._sg_scan = ['bin/sg_scan']
        else:
            self._sg_scan = ['sg_scan', '-i']
    

#######################
# Internal functions
#######################

    def error(self, e):
        assert False, '%s' % e

    def rerror(self, e):
        assert False, 'Mount Error: %s' % e


    def sg_scan(self):
        try:
            p = Popen(self._sg_scan, stdout=PIPE, stderr=PIPE)
            err = p.stderr.read()
            
            if not err:
                ret = p.stdout.read()
                
                if ret.lower().find(self._vendor_name) != -1:
                    return ret
                else:
                    return False

        except Exception, e:
            self.error(e)



    def find_device_id(self):
        try:
            print 'Finding device ID'
            time_out = self._time_out
            if not os.path.exists(self._linux_dev):
                while time_out:
                    lines = self.sg_scan()
                    
                    for line in lines.split('\n'):
                        if line.lower().find(self._vendor_name) != -1:
                            if sys.platform == 'win32':
                                self._device_id = '%s' % line.split(' ')[0]
                            else:
                                self._device_id = '%s' % lines[lines.index(line) -1].split(' ')[0].replace(':', '')
            
                            return self._device_id
                    
                    time_out -= 1
                    sleep(1)

            else:
                self._device_id = self._linux_dev
                return self._device_id
                                
            self.error('Device not found.')
        except Exception, e:
            self.rerror(e)



    def find_mount_point(self, win_label='didj'):
        try:
            print 'Finding mount point'
            timeout = 10
            
            while timeout:
                if sys.platform == 'win32':
                    lines = self.sg_scan()
                    for line in lines.split('\n'):
                        if line.lower().find(self._vendor_name) != -1:
                            line = line.split('[')[1]
                            line = line.split(']')[0]
                            self._mount_point = '%s:\\' % line
                            return self._mount_point
                else:
                    syspath = '/sys/class/scsi_disk'
                    
                    for device in os.listdir(syspath):
                        f = open(os.path.join(syspath, device, 'device/vendor'), 'r')
                        vendor = f.read().split('\n')[0]
                        f.close()
                        
                        if vendor.lower() == self._vendor_name:
                            dev_path = '/dev/%s' % os.listdir(os.path.join(syspath, device, 'device/block'))[0]
                           
                            f = open('/proc/mounts', 'r')
                            
                            for line in f:
                                if line.startswith(dev_path):
                                    self._mount_point = line.split(' ')[1]
                                    f.close()
                                    return self._mount_point
                            f.close()
                sleep(1)
                timeout -= 1
            self.error('Mount not found.')
        except Exception, e:
            self.rerror(e)



#######################
# Connection Interface functions
#######################

    def get_conn_type_i(self):
        return self._conn_type



    def get_root_dir_i(self):
        return self.get_host_id_i()

    

    def set_device_id_i(self, device_id):
        self._device_id = device_id

    def get_device_id_i(self):
        try:
            return self._device_id or self.find_device_id()
        except Exception, e:
            self.error(e)



    def set_host_id_i(self, mount_point):
        self._mount_point = mount_point

    def get_host_id_i(self):
        try:
            return self._mount_point or self.find_mount_point()
        except Exception, e:
            self.error(e)



    def is_connected_i(self):
        try:
            return os.path.exists(self._mount_point)
        except Exception, e:
            self.error(e)

if __name__ == '__main__':
    print 'No examples yet.'