# -*- coding: utf-8 -*-
#!/usr/bin/env python
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#     Anna Chabuda <anna.chabuda@gmail.com>
#

LEVELS_TIMEOUT = 180

LEVELS = { '1': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,0,1,0,1,0,1],
                 [1,1,0,4,0,0,0,0,0,1],
                 [1,0,0,1,0,0,1,0,0,1],
                 [1,3,1,2,0,0,0,0,0,1],
                 [1,0,0,1,0,0,0,0,1,1],
                 [1,1,0,0,1,1,0,0,0,1],
                 [1,0,0,0,0,0,0,1,0,1],
                 [1,0,1,0,0,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

           '2': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,0,0,1,0,0,1],
                 [1,0,0,0,2,0,0,2,1,1],
                 [1,0,1,0,0,0,0,0,0,1],
                 [1,0,0,0,3,0,0,1,0,1],
                 [1,0,0,0,1,0,0,0,0,1],
                 [1,2,0,0,0,0,0,2,0,1],
                 [1,0,0,0,0,0,1,0,0,1],
                 [1,0,1,4,1,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
           '3': [[1,1,1,1,1,1,1,1,1,1],
                 [1,2,0,0,1,0,0,0,2,1],
                 [1,1,0,0,0,0,0,0,1,1],
                 [1,2,0,3,0,0,0,0,1,1],
                 [1,1,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,1,2,1,1],
                 [1,1,0,0,0,0,1,1,1,1],
                 [1,2,0,0,0,0,0,4,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
           '4': [[1,1,1,1,1,1,1,1,1,1],
                 [1,2,0,0,1,0,0,2,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,1,0,4,0,1],
                 [1,1,0,0,0,1,2,0,1,1],
                 [1,2,0,0,3,0,0,0,1,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,1,0,0,0,1,0,1],
                 [1,0,0,2,1,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
           '5': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,1,0,4,0,1],
                 [1,0,0,0,0,0,0,0,2,1],
                 [1,0,0,1,1,0,0,0,0,1],
                 [1,0,0,0,0,0,1,0,0,1],
                 [1,0,1,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,2,0,0,1],
                 [1,1,0,0,3,0,0,0,1,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
           '6': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,2,2,0,0,1,2,1],
                 [1,0,3,0,0,0,0,0,1,1],
                 [1,0,1,0,0,1,0,0,0,1],
                 [1,0,4,0,0,0,0,0,0,1],
                 [1,0,0,2,0,0,0,1,0,1],
                 [1,1,0,0,0,1,0,0,2,1],
                 [1,1,2,1,0,0,0,1,0,1],
                 [1,1,0,0,0,1,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
           '7': [[1,1,1,1,1,1,1,1,1,1],
                 [1,2,1,0,0,3,1,2,0,1],
                 [1,0,0,0,0,0,1,0,0,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,0,0,0,1,1,0,0,0,1],
                 [1,0,0,0,0,0,1,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,2,0,0,0,0,0,4,0,1],
                 [1,0,0,1,0,0,1,1,1,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
           '8': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,0,2,2,2,2,1],
                 [1,3,0,0,0,0,1,1,1,1],
                 [1,0,1,0,0,0,0,2,2,1],
                 [1,0,1,0,0,0,0,1,1,1],
                 [1,0,1,2,0,0,0,0,0,1],
                 [1,0,2,4,0,0,0,0,0,1],
                 [1,0,0,0,0,1,0,0,0,1],
                 [1,1,0,0,0,0,0,1,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
           '9': [[1,1,1,1,1,1,1,1,1,1],
                 [1,1,1,0,0,0,4,0,1,1],
                 [1,1,0,0,2,1,0,0,1,1],
                 [1,1,0,0,1,0,0,0,1,1],
                 [1,1,0,0,3,1,0,0,1,1],
                 [1,1,0,0,0,0,0,1,1,1],
                 [1,1,0,0,1,2,0,0,1,1],
                 [1,1,0,0,1,0,0,0,1,1],
                 [1,1,0,0,0,0,0,0,1,1],
                 [1,1,1,1,1,1,1,1,1,1]], 

            
          '10': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,0,1,0,2,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,1,0,0,0,3,1,0,0,1],
                 [1,0,0,0,1,1,0,0,0,1],
                 [1,0,0,0,1,1,0,0,0,1],
                 [1,0,0,0,0,0,4,0,0,1],
                 [1,2,1,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,1,1,1,1,1,1,1,1,1]],
             
          '11': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,0,1,0,0,0,1],
                 [1,0,0,1,0,0,1,4,0,1],
                 [1,0,1,1,0,0,1,0,2,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,0,0,1,0,0,1,0,0,1],
                 [1,0,3,1,0,0,1,1,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,1,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
          '12': [[1,1,1,1,1,1,1,1,1,1],
                 [1,1,2,0,0,0,1,2,0,1],
                 [1,1,1,0,0,2,1,0,0,1],
                 [1,1,0,0,0,0,0,0,0,1],
                 [1,1,0,3,0,0,1,0,0,1],
                 [1,0,0,0,1,0,2,0,0,1],
                 [1,0,0,1,0,0,0,0,2,1],
                 [1,0,0,0,0,0,0,4,0,1],
                 [1,0,1,0,0,0,1,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
          '13': [[1,1,1,1,1,1,1,1,1,1],
                 [1,2,2,2,0,0,0,0,1,1],
                 [1,0,1,0,0,2,0,0,0,1],
                 [1,0,0,0,0,0,4,0,0,1],
                 [1,0,0,1,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,1,0,3,0,0,1,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,1,1,1,0,0,1,2,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
          '14': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,2,0,0,0,0,1,1],
                 [1,1,0,4,0,0,0,0,0,1],
                 [1,0,0,0,0,1,0,0,0,1],
                 [1,1,0,0,0,0,1,0,0,1],
                 [1,1,1,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,1,0,0,1],
                 [1,0,3,0,0,0,0,0,0,1],
                 [1,0,2,1,1,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '15':  [[1,1,1,1,1,1,1,1,1,1],
                 [1,1,1,1,0,1,1,1,1,1],
                 [1,1,1,0,0,0,0,1,1,1],
                 [1,1,0,3,0,0,0,0,1,1],
                 [1,2,0,0,1,4,0,0,0,1],
                 [1,0,0,0,2,0,0,0,2,1],
                 [1,1,0,0,0,0,0,0,1,1],
                 [1,1,1,0,0,0,1,2,1,1],
                 [1,1,1,1,0,0,1,1,1,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
          '16': [[1,1,1,1,1,1,1,1,1,1],
                 [1,3,0,0,0,0,0,1,1,1],
                 [1,0,1,1,1,1,0,0,1,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,1,1,1,2,1,0,0,0,1],
                 [1,4,0,0,0,0,0,0,1,1],
                 [1,2,0,0,0,0,0,1,1,1],
                 [1,0,0,0,0,0,1,1,1,1],
                 [1,0,0,0,0,1,1,1,1,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
          '17': [[1,1,1,1,1,1,1,1,1,1],
                 [1,3,0,0,0,0,1,2,0,1],
                 [1,0,0,0,1,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,1,0,0,0,0,1,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,1,0,0,0,0,2,1],
                 [1,0,0,0,0,1,4,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
          '18': [[1,1,1,1,1,1,1,1,1,1],
                 [1,1,1,1,2,0,0,0,2,1],
                 [1,0,0,0,0,0,0,0,4,1],
                 [1,0,0,1,1,0,1,0,0,1],
                 [1,0,0,1,0,3,0,0,1,1],
                 [1,0,0,0,0,0,1,0,0,1],
                 [1,2,0,0,0,0,0,1,0,1],
                 [1,1,0,0,0,0,0,0,0,1],
                 [1,1,0,0,2,1,2,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]], 
            
          '19': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,3,0,1,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,1,0,0,1],
                 [1,0,1,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,0,0,1,0,0,0,0,2,1],
                 [1,1,2,0,0,1,0,4,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
          '20': [[1,1,1,1,1,1,1,1,1,1],
                 [1,1,3,0,1,1,1,0,0,1],
                 [1,4,0,0,0,2,1,0,2,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,1,0,1,0,2,1,0,1,1],
                 [1,0,0,0,0,1,1,0,1,1],
                 [1,0,1,0,1,1,0,0,2,1],
                 [1,0,0,0,0,1,0,1,1,1],
                 [1,2,1,0,0,0,0,1,1,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
          '21': [[1,1,1,1,1,1,1,1,1,1],
                 [1,1,4,0,1,1,1,0,0,1],
                 [1,3,0,0,0,0,1,0,2,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,1,0,0,0,0,1,0,1,1],
                 [1,0,0,2,0,1,1,0,1,1],
                 [1,0,1,0,1,1,0,0,2,1],
                 [1,0,0,0,0,1,0,1,1,1],
                 [1,2,1,0,0,0,0,1,1,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
          '22': [[1,1,1,1,1,1,1,1,1,1],
                 [1,1,1,1,1,1,1,1,1,1],
                 [1,1,0,0,0,0,0,3,1,1],
                 [1,1,0,1,1,1,1,0,1,1],
                 [1,1,0,0,0,0,1,0,1,1],
                 [1,1,1,1,1,0,1,0,1,1],
                 [1,2,2,2,1,0,2,0,1,1],
                 [1,2,2,2,1,0,1,1,1,1],
                 [1,2,2,2,1,4,1,2,1,1],
                 [1,1,1,1,1,1,1,1,1,1]],
                            
          '23': [[1,1,1,1,1,1,1,1,1,1],
                 [1,2,0,0,0,1,0,0,2,1],
                 [1,2,0,0,0,0,0,0,1,1],
                 [1,2,0,1,0,0,0,0,2,1],
                 [1,2,3,1,0,0,1,0,2,1],
                 [1,2,0,1,0,0,1,0,2,1],
                 [1,2,0,0,0,0,1,0,2,1],
                 [1,4,0,0,0,0,0,0,2,1],
                 [1,2,0,0,1,0,0,2,2,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
          '24': [[1,1,1,1,1,1,1,1,1,1],
                 [1,1,0,0,0,0,0,0,1,1],
                 [1,0,0,0,0,1,1,0,0,1],
                 [1,1,0,2,0,2,1,1,0,1],
                 [1,0,0,0,3,0,1,1,0,1],
                 [1,0,0,4,0,0,0,2,0,1],
                 [1,0,0,2,0,0,0,1,0,1],
                 [1,0,1,0,1,0,0,0,0,1],
                 [1,0,0,0,0,0,1,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
          '25':  [[1,1,1,1,1,1,1,1,1,1],
                 [1,2,0,0,0,0,0,0,0,1],
                 [1,0,0,4,0,0,0,0,1,1],
                 [1,1,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,1,0,0,3,1],
                 [1,0,2,0,0,0,0,2,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,0,1,0,0,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]], 

            
          '26': [[1,1,1,1,1,1,1,1,1,1],
                 [1,1,1,1,1,1,1,1,1,1],
                 [1,1,3,0,0,1,0,0,1,1],
                 [1,1,0,0,0,0,2,0,1,1],
                 [1,1,0,2,0,0,0,0,1,1],
                 [1,1,0,0,0,0,1,0,1,1],
                 [1,1,0,0,1,0,0,4,1,1],
                 [1,1,0,0,0,1,0,0,1,1],
                 [1,1,1,1,1,1,1,1,1,1],
                 [1,1,1,1,1,1,1,1,1,1]], 
            
          '27': [[1,1,1,1,1,1,1,1,1,1],
                 [1,1,2,0,0,0,0,0,0,1],
                 [1,0,0,0,0,1,2,0,0,1],
                 [1,0,1,0,0,0,0,0,0,1],
                 [1,0,2,0,2,0,2,0,0,1],
                 [1,3,0,0,0,0,1,0,0,1],
                 [1,0,0,0,0,0,0,4,0,1],
                 [1,0,0,1,2,0,0,2,0,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '28': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,1,2,0,0,0,0,1],
                 [1,0,0,0,0,0,1,1,0,1],
                 [1,0,1,1,0,1,0,0,0,1],
                 [1,0,0,0,0,2,0,0,0,1],
                 [1,2,1,0,0,0,0,2,0,1],
                 [1,0,1,3,0,0,0,1,0,1],
                 [1,0,1,1,1,0,1,1,0,1],
                 [1,4,0,0,0,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]], 

          '29': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,1,4,2,2,2,3,0,1],
                 [1,0,0,0,2,1,0,0,0,1],
                 [1,1,0,0,0,0,0,0,0,1],
                 [1,0,0,0,1,0,0,0,0,1],
                 [1,0,0,2,1,0,0,0,0,1],
                 [1,0,1,0,0,0,2,0,1,1],
                 [1,0,0,2,0,1,0,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '30': [[1,1,1,1,1,1,1,1,1,1],
                 [1,1,1,1,0,0,1,1,1,1],
                 [1,1,1,0,0,0,0,1,1,1],
                 [1,1,0,0,0,0,0,0,1,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,4,0,0,0,0,0,1,1,1],
                 [1,1,1,0,0,0,1,1,1,1],
                 [1,1,1,1,3,1,1,1,1,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '31': [[1,1,1,1,1,1,1,1,1,1],
                 [1,2,0,0,1,1,0,0,2,1],
                 [1,0,0,1,0,0,0,1,1,1],
                 [1,1,0,0,0,0,0,1,2,1],
                 [1,0,0,0,3,0,0,0,0,1],
                 [1,1,0,0,0,4,0,0,0,1],
                 [1,0,1,0,0,0,0,0,0,1],
                 [1,0,1,0,0,0,0,0,0,1],
                 [1,0,0,0,0,1,1,1,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],


          '32': [[1,1,1,1,1,1,1,1,1,1],
                 [1,4,0,0,0,2,0,0,1,1],
                 [1,0,0,1,0,0,1,0,0,1],
                 [1,2,0,0,0,1,0,0,0,1],
                 [1,1,1,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,0,1,0,0,0,3,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,1,0,0,0,0,1,1,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '33': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,1,0,0,1,0,1],
                 [1,1,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,1,0,0,3,0,0,0,0,1],
                 [1,2,0,0,1,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,0,1,4,0,1,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '34': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,0,1,0,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,3,0,0,1,0,2,0,0,1],
                 [1,0,1,0,0,0,0,4,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,1,0,0,1,1],
                 [1,0,0,1,1,2,0,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '35':  [[1,1,1,1,1,1,1,1,1,1],
                 [1,1,0,0,1,1,0,0,0,1],
                 [1,0,0,0,0,0,0,2,2,1],
                 [1,0,3,0,0,0,0,0,0,1],
                 [1,0,0,0,1,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,1,0,2,0,0,0,0,2,1],
                 [1,4,0,0,0,0,0,0,0,1],
                 [1,2,0,0,1,1,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

     
          '36': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,1,0,0,1,0,0,1],
                 [1,0,1,0,0,0,1,1,0,1],
                 [1,4,0,0,0,0,0,0,1,1],
                 [1,2,0,3,1,0,1,0,0,1],
                 [1,0,0,0,0,0,2,0,0,1],
                 [1,1,2,0,0,0,0,0,0,1],
                 [1,0,0,1,2,0,0,0,0,1],
                 [1,0,0,0,0,0,1,2,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
          '37': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,2,0,0,0,0,0,1,1],
                 [1,0,0,4,0,0,0,0,0,1],
                 [1,1,0,1,1,0,1,2,0,1],
                 [1,0,0,0,1,0,0,1,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,1,0,0,0,0,1,1],
                 [1,3,0,0,0,0,1,0,0,1],
                 [1,1,0,0,0,0,0,0,2,1],
                 [1,1,1,1,1,1,1,1,1,1]], 
            
          '38': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,1,1,0,0,0,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,0,1,2,0,0,0,0,0,1],
                 [1,0,0,0,0,4,0,0,0,1],
                 [1,0,0,0,3,0,0,0,0,1],
                 [1,1,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,1,0,1],
                 [1,0,0,0,0,1,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]], 
            
          '39': [[1,1,1,1,1,1,1,1,1,1],
                 [1,2,1,0,0,0,0,0,0,1],
                 [1,0,0,0,1,0,0,0,0,1],
                 [1,0,0,0,0,1,0,0,0,1],
                 [1,0,0,0,3,0,0,1,0,1],
                 [1,0,0,0,0,0,0,4,0,1],
                 [1,0,0,0,0,0,0,0,2,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,0,1,1,0,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '40': [[1,1,1,1,1,1,1,1,1,1],
                 [1,1,0,1,4,0,0,2,0,1],
                 [1,2,0,0,0,0,0,0,0,1],
                 [1,3,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,1,0,0,0,1],
                 [1,0,1,0,0,0,0,0,0,1],
                 [1,0,0,1,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,1,0,1],
                 [1,0,0,0,1,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '41': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,2,1,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,1,0,1],
                 [1,0,0,0,2,0,0,1,0,1],
                 [1,0,0,0,0,2,0,0,0,1],
                 [1,1,0,0,0,0,0,0,0,1],
                 [1,2,0,3,0,0,1,1,0,1],
                 [1,0,0,2,0,0,0,0,0,1],
                 [1,0,0,4,0,2,1,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '42': [[1,1,1,1,1,1,1,1,1,1],
                 [1,1,0,1,0,1,1,0,0,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,0,0,1,0,0,0,0,2,1],
                 [1,0,0,0,4,0,0,0,0,1],
                 [1,2,0,0,0,3,0,0,0,1],
                 [1,0,0,0,0,0,0,1,0,1],
                 [1,1,0,0,0,0,2,0,0,1],
                 [1,0,0,0,1,1,1,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '43': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,1,0,0,0,0,1],
                 [1,0,0,1,0,0,1,0,0,1],
                 [1,0,0,0,0,0,0,4,0,1],
                 [1,0,0,0,0,0,0,2,0,1],
                 [1,0,0,0,3,0,0,0,1,1],
                 [1,0,1,0,0,0,0,0,0,1],
                 [1,0,0,0,0,1,0,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '44': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,0,1,0,0,4,1],
                 [1,0,0,0,0,0,0,0,2,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,1,0,0,0,0,1,0,1],
                 [1,0,0,0,1,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,3,0,0,0,0,1,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],
            
          '45':  [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,0,1,0,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,1,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,3,2,4,0,0,0,1],
                 [1,0,0,0,0,2,1,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,1,1,0,0,0,2,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '46': [[1,1,1,1,1,1,1,1,1,1],
                 [1,1,0,0,0,0,0,1,0,1],
                 [1,0,0,0,0,1,0,0,0,1],
                 [1,0,0,0,0,0,0,0,4,1],
                 [1,3,0,0,2,2,2,0,0,1],
                 [1,0,0,1,0,0,0,0,0,1],
                 [1,0,2,0,0,0,0,1,0,1],
                 [1,0,0,0,0,2,0,0,0,1],
                 [1,0,0,0,1,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '47': [[1,1,1,1,1,1,1,1,1,1],
                 [1,2,2,4,2,2,2,2,2,1],
                 [1,1,1,0,0,0,1,0,2,1],
                 [1,0,0,0,0,1,0,0,2,1],
                 [1,3,0,0,0,0,0,1,2,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,2,0,0,1,0,2,0,2,1],
                 [1,2,1,0,0,0,0,0,2,1],
                 [1,2,2,2,2,2,2,1,2,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '48': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,0,0,1,0,4,1],
                 [1,0,0,0,0,0,0,0,2,1],
                 [1,0,0,0,1,0,0,0,0,1],
                 [1,0,0,1,0,0,0,0,1,1],
                 [1,0,1,0,0,0,0,1,0,1],
                 [1,1,0,0,0,1,0,0,0,1],
                 [1,0,0,0,1,0,0,0,0,1],
                 [1,3,0,1,0,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '49': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,1,4,0,2,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,1,0,0,1],
                 [1,0,1,0,0,0,0,0,0,1],
                 [1,0,0,0,3,0,0,0,0,1],
                 [1,0,0,0,0,0,0,1,0,1],
                 [1,0,0,0,1,0,0,0,0,1],
                 [1,2,1,0,0,0,1,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '50': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,2,1,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,3,0,1],
                 [1,0,4,1,0,1,0,0,0,1],
                 [1,0,0,1,0,0,0,1,0,1],
                 [1,0,0,1,0,0,0,0,1,1],
                 [1,2,0,1,1,2,0,0,2,1],
                 [1,1,0,0,0,0,0,0,0,1],
                 [1,0,0,1,2,0,0,1,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '51': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,0,1,1,1,1,0,0,2,1],
                 [1,0,1,3,0,1,1,0,0,1],
                 [1,0,1,1,0,1,0,0,4,1],
                 [1,0,0,0,0,1,0,0,2,1],
                 [1,0,1,1,1,1,0,0,0,1],
                 [1,0,0,0,0,2,0,0,0,1],
                 [1,0,0,0,0,0,0,1,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '52': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,2,0,0,0,0,0,0,1],
                 [1,1,2,0,1,1,0,0,0,1],
                 [1,0,0,0,1,1,2,0,0,1],
                 [1,0,1,1,1,1,1,1,0,1],
                 [1,0,1,1,1,1,1,1,0,1],
                 [1,0,2,0,1,1,4,0,0,1],
                 [1,0,0,0,1,1,0,2,1,1],
                 [1,3,0,0,0,0,0,2,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '53': [[1,1,1,1,1,1,1,1,1,1],
                 [1,2,1,0,0,0,0,1,2,1],
                 [1,0,1,0,0,3,0,0,1,1],
                 [1,0,0,1,0,0,0,0,1,1],
                 [1,0,1,0,0,0,0,1,0,1],
                 [1,0,4,0,0,0,0,0,1,1],
                 [1,0,0,1,0,0,0,0,1,1],
                 [1,0,2,0,1,0,0,1,0,1],
                 [1,0,0,0,0,0,0,2,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '54': [[1,1,1,1,1,1,1,1,1,1],
                 [1,3,0,0,0,0,0,0,0,1],
                 [1,0,1,0,0,2,0,0,0,1],
                 [1,0,0,0,0,0,0,1,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,4,0,0,0,0,0,1],
                 [1,0,0,0,0,0,1,0,0,1],
                 [1,1,0,0,0,0,2,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '55':  [[1,1,1,1,1,1,1,1,1,1],
                 [1,2,1,1,1,0,0,0,0,1],
                 [1,0,0,0,0,0,1,1,0,1],
                 [1,0,1,0,1,0,1,1,1,1],
                 [1,0,1,3,1,0,1,0,0,1],
                 [1,0,0,1,0,0,0,0,1,1],
                 [1,1,1,4,1,1,1,0,1,1],
                 [1,1,1,0,1,1,1,0,1,1],
                 [1,1,1,0,0,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '56': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,1,0,0,1,0,0,1],
                 [1,0,1,4,0,0,0,0,0,1],
                 [1,2,0,0,0,0,0,1,0,1],
                 [1,1,0,0,0,0,0,0,2,1],
                 [1,0,0,0,0,0,0,0,1,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,3,0,0,0,1,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '57': [[1,1,1,1,1,1,1,1,1,1],
                 [1,2,1,2,1,2,1,2,1,1],
                 [1,3,0,0,1,0,0,0,0,1],
                 [1,0,1,0,0,0,0,1,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,0,0,4,0,1],
                 [1,0,0,0,0,1,0,0,1,1],
                 [1,1,2,1,2,1,2,1,2,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '58': [[1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,0,0,0,1,0,1],
                 [1,0,2,1,0,0,0,2,0,1],
                 [1,0,0,3,0,0,0,0,0,1],
                 [1,1,0,0,0,0,0,0,0,1],
                 [1,0,0,1,0,0,0,0,1,1],
                 [1,0,0,4,0,1,0,0,0,1],
                 [1,0,2,0,0,0,1,2,0,1],
                 [1,0,1,0,0,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '59': [[1,1,1,1,1,1,1,1,1,1],
                 [1,3,0,0,0,0,0,1,2,1],
                 [1,2,2,2,2,2,0,2,0,1],
                 [1,2,4,2,2,2,0,2,0,1],
                 [1,2,0,2,0,0,0,0,0,1],
                 [1,2,0,2,2,2,1,2,0,1],
                 [1,2,0,1,0,0,0,0,0,1],
                 [1,2,0,2,0,2,2,2,1,1],
                 [1,1,0,0,0,0,0,0,2,1],
                 [1,1,1,1,1,1,1,1,1,1]],

          '60': [[1,1,1,1,1,1,1,1,1,1],
                 [1,1,0,0,1,1,0,0,0,1],
                 [1,2,0,3,1,0,0,1,0,1],
                 [1,0,0,0,0,0,1,1,0,1],
                 [1,0,1,0,0,1,1,0,0,1],
                 [1,0,0,1,1,1,0,0,1,1],
                 [1,1,0,2,1,0,0,1,1,1],
                 [1,2,0,0,4,0,1,1,1,1],
                 [1,2,1,2,1,1,1,1,1,1],
                 [1,1,1,1,1,1,1,1,1,1]]
                 }

LEVELS_IN_ORDER={ '1':(LEVELS['3'], 'N'), 
                  '2':(LEVELS['3'], 'T->'),  
                  '3':(LEVELS['4'], 'N'),  
                  '4':(LEVELS['7'], 'N'),  
                  '5':(LEVELS['3'], 'T'),  
                  '6':(LEVELS['4'], 'T')  ,
                  '7':(LEVELS['10'], 'T->'),  
                  '8':(LEVELS['7'], 'T->'), 
                  '9':(LEVELS['7'], 'T'), 
                  '10':(LEVELS['10'], 'T'), 
                  '11':(LEVELS['22'], 'T->'), 
                  '12':(LEVELS['11'], 'N'), 
                  '13':(LEVELS['22'], 'T'), 
                  '14':(LEVELS['8'], 'N'), 
                  '15':(LEVELS['22'], 'N'), 
                  '16':(LEVELS['21'], 'N'),
                  '17':(LEVELS['11'], 'T'), 
                  '18':(LEVELS['14'], 'T'), 
                  '19':(LEVELS['15'], 'T->'), 
                  '20':(LEVELS['13'], 'T->'),  
                  '21':(LEVELS['6'], 'N'), 
                  '22':(LEVELS['5'], 'T->'), 
                  '23':(LEVELS['6'], 'T'), 
                  '24':(LEVELS['4'], 'T->'), 
                  '25':(LEVELS['11'], 'T->'),
                  '26':(LEVELS['15'], 'N'),
                  '27':(LEVELS['26'], 'T'),
                  '28':(LEVELS['26'], 'T->'),
                  '29':(LEVELS['5'], 'N'),
                  '30':(LEVELS['9'], 'N'),
                  '31':(LEVELS['20'], 'N'),
                  '32':(LEVELS['23'], 'T->'),
                  '33':(LEVELS['17'], 'N'),
                  '34':(LEVELS['12'], 'N'),
                  '35':(LEVELS['17'], 'T->'),
                  '36':(LEVELS['12'], 'T'),
                  '37':(LEVELS['10'], 'N'),
                  '38':(LEVELS['14'], 'T->'),
                  '39':(LEVELS['9'], 'T->'),
                  '40':(LEVELS['23'], 'N'),
                  '41':(LEVELS['28'], 'T->'),
                  '42':(LEVELS['8'], 'T'),
                  '43':(LEVELS['35'], 'T->'),
                  '44':(LEVELS['23'], 'T'),
                  '45':(LEVELS['51'], 'N'),
                  '46':(LEVELS['26'], 'N'),
                  '47':(LEVELS['6'], 'T->'),
                  '48':(LEVELS['52'], 'N'),
                  '49':(LEVELS['55'], 'T'),
                  '50':(LEVELS['52'], 'T->'),
                  '51':(LEVELS['20'], 'T'),
                  '52':(LEVELS['51'], 'T->'),
                  '53':(LEVELS['28'], 'N'),
                  '54':(LEVELS['28'], 'T'),
                  '55':(LEVELS['12'], 'T->'),
                  '56':(LEVELS['51'], 'T'),
                  '57':(LEVELS['29'], 'T'),
                  '58':(LEVELS['29'], 'T->'),
                  '59':(LEVELS['55'], 'N'),
                  '60':(LEVELS['36'], 'T'),
                  '61':(LEVELS['36'], 'N'),
                  '62':(LEVELS['55'], 'T->'),
                  '63':(LEVELS['16'], 'N'),
                  '64':(LEVELS['17'], 'T'),
                  '65':(LEVELS['59'], 'T'),
                  '66':(LEVELS['16'], 'T'),
                  '67':(LEVELS['59'], 'N'),
                  '68':(LEVELS['9'], 'T'),
                  '69':(LEVELS['44'], 'T'),
                  '70':(LEVELS['52'], 'T'),
                  '71':(LEVELS['36'], 'T->'),
                  '72':(LEVELS['14'], 'N'),
                  '73':(LEVELS['44'], 'T->'),
                  '74':(LEVELS['16'], 'T->'),
                  '75':(LEVELS['35'], 'T'),
                  '76':(LEVELS['60'], 'N'),
                  '77':(LEVELS['29'], 'N'),
                  '78':(LEVELS['21'], 'T->'),
                  '79':(LEVELS['59'], 'T->'),
                  '80':(LEVELS['44'], 'N'),
                  '81':(LEVELS['19'], 'T'),
                  '82':(LEVELS['13'], 'N'),
                  '83':(LEVELS['45'], 'N'),
                  '84':(LEVELS['32'], 'N'),
                  '85':(LEVELS['46'], 'N'),
                  '86':(LEVELS['40'], 'T'),
                  '87':(LEVELS['8'], 'T->'),
                  '88':(LEVELS['60'], 'T'),
                  '89':(LEVELS['46'], 'T->'),
                  '90':(LEVELS['21'], 'T'),
                  '91':(LEVELS['25'], 'N'),
                  '92':(LEVELS['30'], 'N'),
                  '93':(LEVELS['57'], 'T->'),
                  '94':(LEVELS['60'], 'T->'),
                  '95':(LEVELS['34'], 'T->'),
                  '96':(LEVELS['15'], 'T'),
                  '97':(LEVELS['20'], 'T->'),
                  '98':(LEVELS['5'], 'T'),
                  '99':(LEVELS['46'], 'T'),
                  '100':(LEVELS['1'], 'T->'),
                  '101':(LEVELS['35'], 'N'),
                  '102':(LEVELS['57'], 'N'),
                  '103':(LEVELS['48'], 'T->'),
                  '104':(LEVELS['45'], 'T->'),
                  '105':(LEVELS['30'], 'T->'),
                  '106':(LEVELS['37'], 'N'),
                  '107':(LEVELS['56'], 'T->'),
                  '108':(LEVELS['58'], 'N'),
                  '109':(LEVELS['58'], 'T->'),
                  '110':(LEVELS['53'], 'T->'),
                  '111':(LEVELS['56'], 'T'),
                  '112':(LEVELS['32'], 'T'),
                  '113':(LEVELS['30'], 'T'),
                  '114':(LEVELS['40'], 'T->'),
                  '115':(LEVELS['49'], 'T'),
                  '116':(LEVELS['25'], 'T->'),
                  '117':(LEVELS['37'], 'T'),
                  '118':(LEVELS['49'], 'N'),
                  '119':(LEVELS['19'], 'N'),
                  '120':(LEVELS['50'], 'T->'),
                  '121':(LEVELS['13'], 'T'),
                  '122':(LEVELS['18'], 'T->'),
                  '123':(LEVELS['54'], 'T->'),
                  '124':(LEVELS['53'], 'T'),
                  '125':(LEVELS['43'], 'N'),
                  '126':(LEVELS['18'], 'N'),
                  '127':(LEVELS['1'], 'N'),
                  '128':(LEVELS['41'], 'N'),
                  '129':(LEVELS['57'], 'T'),
                  '130':(LEVELS['48'], 'T'),
                  '131':(LEVELS['53'], 'N'),
                  '132':(LEVELS['19'], 'T->'),
                  '133':(LEVELS['40'], 'N'),
                  '134':(LEVELS['18'], 'T'),
                  '135':(LEVELS['50'], 'N'),
                  '136':(LEVELS['45'], 'T'),
                  '137':(LEVELS['1'], 'T'),
                  '138':(LEVELS['38'], 'T->'),
                  '139':(LEVELS['56'], 'N'),
                  '140':(LEVELS['54'], 'T'),
                  '141':(LEVELS['42'], 'T'),
                  '142':(LEVELS['41'], 'T->'),
                  '143':(LEVELS['25'], 'T'),
                  '144':(LEVELS['50'], 'T'),
                  '145':(LEVELS['34'], 'N'),
                  '146':(LEVELS['33'], 'T->'),
                  '147':(LEVELS['41'], 'T'),
                  '148':(LEVELS['32'], 'T->'),
                  '149':(LEVELS['54'], 'N'),
                  '150':(LEVELS['48'], 'N'),
                  '151':(LEVELS['47'], 'T->'),
                  '152':(LEVELS['49'], 'T->'),
                  '153':(LEVELS['38'], 'T'),
                  '154':(LEVELS['43'], 'T'),
                  '155':(LEVELS['43'], 'T->'),
                  '156':(LEVELS['37'], 'T->'),
                  '157':(LEVELS['2'], 'T'),
                  '158':(LEVELS['2'], 'N'),
                  '159':(LEVELS['2'], 'T->'),
                  '160':(LEVELS['39'], 'T->'),
                  '161':(LEVELS['58'], 'T'),
                  '162':(LEVELS['42'], 'T->'),
                  '163':(LEVELS['33'], 'N'),
                  '164':(LEVELS['47'], 'N'),
                  '165':(LEVELS['34'], 'T'),
                  '166':(LEVELS['31'], 'T')}
