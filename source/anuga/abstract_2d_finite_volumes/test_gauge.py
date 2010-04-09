#!/usr/bin/env python


import unittest
from math import sqrt, pi
import tempfile, os
from os import access, F_OK,sep, removedirs,remove,mkdir,getcwd

#from anuga.abstract_2d_finite_volumes.util import *
from anuga.abstract_2d_finite_volumes.gauge import *
from anuga.config import epsilon
from anuga.shallow_water.data_manager import timefile2netcdf,del_dir

from anuga.utilities.numerical_tools import NAN,mean

from sys import platform 

from anuga.pmesh.mesh import Mesh
from anuga.shallow_water import Domain, Transmissive_boundary
from anuga.shallow_water.data_manager import SWW_file
from csv import reader,writer
import time
import string

import numpy as num


def test_function(x, y):
    return x+y

class Test_Util(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sww2csv(self):

        def elevation_function(x, y):
            return -x
        
        """Most of this test was copied from test_interpolate
        test_interpole_sww2csv
        
        This is testing the sww2csv_gauges function, by creating a sww file and
        then exporting the gauges and checking the results.
        """
        
        # Create mesh
        mesh_file = tempfile.mktemp(".tsh")    
        points = [[0.0,0.0],[6.0,0.0],[6.0,6.0],[0.0,6.0]]
        m = Mesh()
        m.add_vertices(points)
        m.auto_segment()
        m.generate_mesh(verbose=False)
        m.export_mesh_file(mesh_file)
        
        # Create shallow water domain
        domain = Domain(mesh_file)
        os.remove(mesh_file)
        
        domain.default_order=2
        
        # This test was made before tight_slope_limiters were introduced
        # Since were are testing interpolation values this is OK
        domain.tight_slope_limiters = 0 
        

        # Set some field values
        domain.set_quantity('elevation', elevation_function)
        domain.set_quantity('friction', 0.03)
        domain.set_quantity('xmomentum', 3.0)
        domain.set_quantity('ymomentum', 4.0)

        ######################
        # Boundary conditions
        B = Transmissive_boundary(domain)
        domain.set_boundary( {'exterior': B})

        # This call mangles the stage values.
        domain.distribute_to_vertices_and_edges()
        domain.set_quantity('stage', 1.0)


        domain.set_name('datatest' + str(time.time()))
        domain.smooth = True
        domain.reduction = mean


        sww = SWW_file(domain)
        sww.store_connectivity()
        sww.store_timestep()
        domain.set_quantity('stage', 10.0) # This is automatically limited
        # so it will not be less than the elevation
        domain.time = 2.
        sww.store_timestep()

        # test the function
        points = [[5.0,1.],[0.5,2.]]

        points_file = tempfile.mktemp(".csv")
#        points_file = 'test_point.csv'
        file_id = open(points_file,"w")
        file_id.write("name, easting, northing, elevation \n\
point1, 5.0, 1.0, 3.0\n\
point2, 0.5, 2.0, 9.0\n")
        file_id.close()

        
        sww2csv_gauges(sww.filename, 
                       points_file,
                       verbose=False,
                       use_cache=False)

#        point1_answers_array = [[0.0,1.0,-5.0,3.0,4.0], [2.0,10.0,-5.0,3.0,4.0]]
        point1_answers_array = [[0.0,0.0,1.0,6.0,-5.0,3.0,4.0], [2.0,2.0/3600.,10.0,15.0,-5.0,3.0,4.0]]
        point1_filename = 'gauge_point1.csv'
        point1_handle = file(point1_filename)
        point1_reader = reader(point1_handle)
        point1_reader.next()

        line=[]
        for i,row in enumerate(point1_reader):
#            print 'i',i,'row',row
            line.append([float(row[0]),float(row[1]),float(row[2]),float(row[3]),
                         float(row[4]),float(row[5]),float(row[6])])
#            print 'assert line',line[i],'point1',point1_answers_array[i]
            assert num.allclose(line[i], point1_answers_array[i])

        point2_answers_array = [[0.0,0.0,1.0,1.5,-0.5,3.0,4.0], [2.0,2.0/3600.,10.0,10.5,-0.5,3.0,4.0]]
        point2_filename = 'gauge_point2.csv' 
        point2_handle = file(point2_filename)
        point2_reader = reader(point2_handle)
        point2_reader.next()
                        
        line=[]
        for i,row in enumerate(point2_reader):
#            print 'i',i,'row',row
            line.append([float(row[0]),float(row[1]),float(row[2]),float(row[3]),
                         float(row[4]),float(row[5]),float(row[6])])
#            print 'assert line',line[i],'point1',point1_answers_array[i]
            assert num.allclose(line[i], point2_answers_array[i])
                         
        # clean up
        point1_handle.close()
        point2_handle.close()
        #print "sww.filename",sww.filename 
        os.remove(sww.filename)
        os.remove(points_file)
        os.remove(point1_filename)
        os.remove(point2_filename)


    def test_sww2csv_gauges1(self):
        from anuga.pmesh.mesh import Mesh
        from anuga.shallow_water import Domain, Transmissive_boundary
        from csv import reader,writer
        import time
        import string

        def elevation_function(x, y):
            return -x
        
        """Most of this test was copied from test_interpolate
        test_interpole_sww2csv
        
        This is testing the sww2csv_gauges function, by creating a sww file and
        then exporting the gauges and checking the results.
        
        This tests the ablity not to have elevation in the points file and 
        not store xmomentum and ymomentum
        """
        
        # Create mesh
        mesh_file = tempfile.mktemp(".tsh")    
        points = [[0.0,0.0],[6.0,0.0],[6.0,6.0],[0.0,6.0]]
        m = Mesh()
        m.add_vertices(points)
        m.auto_segment()
        m.generate_mesh(verbose=False)
        m.export_mesh_file(mesh_file)
        
        # Create shallow water domain
        domain = Domain(mesh_file)
        os.remove(mesh_file)
        
        domain.default_order=2

        # Set some field values
        domain.set_quantity('elevation', elevation_function)
        domain.set_quantity('friction', 0.03)
        domain.set_quantity('xmomentum', 3.0)
        domain.set_quantity('ymomentum', 4.0)

        ######################
        # Boundary conditions
        B = Transmissive_boundary(domain)
        domain.set_boundary( {'exterior': B})

        # This call mangles the stage values.
        domain.distribute_to_vertices_and_edges()
        domain.set_quantity('stage', 1.0)


        domain.set_name('datatest' + str(time.time()))
        domain.smooth = True
        domain.reduction = mean

        sww = SWW_file(domain)
        sww.store_connectivity()
        sww.store_timestep()
        domain.set_quantity('stage', 10.0) # This is automatically limited
        # so it will not be less than the elevation
        domain.time = 2.
        sww.store_timestep()

        # test the function
        points = [[5.0,1.],[0.5,2.]]

        points_file = tempfile.mktemp(".csv")
#        points_file = 'test_point.csv'
        file_id = open(points_file,"w")
        file_id.write("name,easting,northing \n\
point1, 5.0, 1.0\n\
point2, 0.5, 2.0\n")
        file_id.close()

        sww2csv_gauges(sww.filename, 
                            points_file,
                            quantities=['stage', 'elevation'],
                            use_cache=False,
                            verbose=False)

        point1_answers_array = [[0.0,1.0,-5.0], [2.0,10.0,-5.0]]
        point1_filename = 'gauge_point1.csv'
        point1_handle = file(point1_filename)
        point1_reader = reader(point1_handle)
        point1_reader.next()

        line=[]
        for i,row in enumerate(point1_reader):
#            print 'i',i,'row',row
            # note the 'hole' (element 1) below - skip the new 'hours' field
            line.append([float(row[0]),float(row[2]),float(row[3])])
            #print 'line',line[i],'point1',point1_answers_array[i]
            assert num.allclose(line[i], point1_answers_array[i])

        point2_answers_array = [[0.0,1.0,-0.5], [2.0,10.0,-0.5]]
        point2_filename = 'gauge_point2.csv' 
        point2_handle = file(point2_filename)
        point2_reader = reader(point2_handle)
        point2_reader.next()
                        
        line=[]
        for i,row in enumerate(point2_reader):
#            print 'i',i,'row',row
            # note the 'hole' (element 1) below - skip the new 'hours' field
            line.append([float(row[0]),float(row[2]),float(row[3])])
#            print 'line',line[i],'point1',point1_answers_array[i]
            assert num.allclose(line[i], point2_answers_array[i])
                         
        # clean up
        point1_handle.close()
        point2_handle.close()
        #print "sww.filename",sww.filename 
        os.remove(sww.filename)
        os.remove(points_file)
        os.remove(point1_filename)
        os.remove(point2_filename)


    def test_sww2csv_gauges2(self):

        def elevation_function(x, y):
            return -x
        
        """Most of this test was copied from test_interpolate
        test_interpole_sww2csv
        
        This is testing the sww2csv_gauges function, by creating a sww file and
        then exporting the gauges and checking the results.
        
        This is the same as sww2csv_gauges except set domain.set_starttime to 5.
        Therefore testing the storing of the absolute time in the csv files
        """
        
        # Create mesh
        mesh_file = tempfile.mktemp(".tsh")    
        points = [[0.0,0.0],[6.0,0.0],[6.0,6.0],[0.0,6.0]]
        m = Mesh()
        m.add_vertices(points)
        m.auto_segment()
        m.generate_mesh(verbose=False)
        m.export_mesh_file(mesh_file)
        
        # Create shallow water domain
        domain = Domain(mesh_file)
        os.remove(mesh_file)
        
        domain.default_order=2

        # This test was made before tight_slope_limiters were introduced
        # Since were are testing interpolation values this is OK
        domain.tight_slope_limiters = 0         

        # Set some field values
        domain.set_quantity('elevation', elevation_function)
        domain.set_quantity('friction', 0.03)
        domain.set_quantity('xmomentum', 3.0)
        domain.set_quantity('ymomentum', 4.0)
        domain.set_starttime(5)

        ######################
        # Boundary conditions
        B = Transmissive_boundary(domain)
        domain.set_boundary( {'exterior': B})

        # This call mangles the stage values.
        domain.distribute_to_vertices_and_edges()
        domain.set_quantity('stage', 1.0)
        


        domain.set_name('datatest' + str(time.time()))
        domain.smooth = True
        domain.reduction = mean

        sww = SWW_file(domain)
        sww.store_connectivity()
        sww.store_timestep()
        domain.set_quantity('stage', 10.0) # This is automatically limited
        # so it will not be less than the elevation
        domain.time = 2.
        sww.store_timestep()

        # test the function
        points = [[5.0,1.],[0.5,2.]]

        points_file = tempfile.mktemp(".csv")
#        points_file = 'test_point.csv'
        file_id = open(points_file,"w")
        file_id.write("name, easting, northing, elevation \n\
point1, 5.0, 1.0, 3.0\n\
point2, 0.5, 2.0, 9.0\n")
        file_id.close()

        
        sww2csv_gauges(sww.filename, 
                            points_file,
                            verbose=False,
                            use_cache=False)

#        point1_answers_array = [[0.0,1.0,-5.0,3.0,4.0], [2.0,10.0,-5.0,3.0,4.0]]
        point1_answers_array = [[5.0,5.0/3600.,1.0,6.0,-5.0,3.0,4.0], [7.0,7.0/3600.,10.0,15.0,-5.0,3.0,4.0]]
        point1_filename = 'gauge_point1.csv'
        point1_handle = file(point1_filename)
        point1_reader = reader(point1_handle)
        point1_reader.next()

        line=[]
        for i,row in enumerate(point1_reader):
            #print 'i',i,'row',row
            line.append([float(row[0]),float(row[1]),float(row[2]),float(row[3]),
                         float(row[4]), float(row[5]), float(row[6])])
            #print 'assert line',line[i],'point1',point1_answers_array[i]
            assert num.allclose(line[i], point1_answers_array[i])

        point2_answers_array = [[5.0,5.0/3600.,1.0,1.5,-0.5,3.0,4.0], [7.0,7.0/3600.,10.0,10.5,-0.5,3.0,4.0]]
        point2_filename = 'gauge_point2.csv' 
        point2_handle = file(point2_filename)
        point2_reader = reader(point2_handle)
        point2_reader.next()
                        
        line=[]
        for i,row in enumerate(point2_reader):
            #print 'i',i,'row',row
            line.append([float(row[0]),float(row[1]),float(row[2]),float(row[3]),
                         float(row[4]),float(row[5]), float(row[6])])
            #print 'assert line',line[i],'point1',point1_answers_array[i]
            assert num.allclose(line[i], point2_answers_array[i])
                         
        # clean up
        point1_handle.close()
        point2_handle.close()
        #print "sww.filename",sww.filename 
        os.remove(sww.filename)
        os.remove(points_file)
        os.remove(point1_filename)
        os.remove(point2_filename)
		

    def test_sww2csv_centroid(self):

        def elevation_function(x, y):
            return -x
        
        """Check sww2csv timeseries at centroid.
        
        Test the ability to get a timeseries at the centroid of a triangle, rather
		than the given gauge point.
        """
        
        # Create rectangular mesh
        mesh_file = tempfile.mktemp(".tsh")    
        points = [[0.0,0.0],[6.0,0.0],[6.0,6.0],[0.0,6.0]]
        m = Mesh()
        m.add_vertices(points)
        m.auto_segment()
        m.generate_mesh(verbose=False)
        m.export_mesh_file(mesh_file)
        
        # Create shallow water domain
        domain = Domain(mesh_file)
        
        domain.default_order=2
        
        # This test was made before tight_slope_limiters were introduced
        # Since were are testing interpolation values this is OK
        domain.tight_slope_limiters = 0 
        

        # Set some field values
        domain.set_quantity('elevation', elevation_function)
        domain.set_quantity('friction', 0.03)
        domain.set_quantity('xmomentum', 3.0)
        domain.set_quantity('ymomentum', 4.0)

        ######################
        # Boundary conditions
        B = Transmissive_boundary(domain)
        domain.set_boundary( {'exterior': B})

        # This call mangles the stage values.
        domain.distribute_to_vertices_and_edges()
        domain.set_quantity('stage', 1.0)


        domain.set_name('datatest' + str(time.time()))
        domain.smooth = True
        domain.reduction = mean


        sww = SWW_file(domain)
        sww.store_connectivity()
        sww.store_timestep()
        domain.set_quantity('stage', 10.0) # This is automatically limited
        # so it will not be less than the elevation
        domain.time = 2.
        sww.store_timestep()

        # create a csv file containing our gauge points
        points_file = tempfile.mktemp(".csv")
        file_id = open(points_file,"w")
# These values are where the centroids should be		
#        file_id.write("name, easting, northing, elevation \n\
#point1, 2.0, 2.0, 3.0\n\
#point2, 4.0, 4.0, 9.0\n")
 
# These values are slightly off the centroids - will it find the centroids?
        file_id.write("name, easting, northing, elevation \n\
point1, 2.0, 1.0, 3.0\n\
point2, 4.5, 4.0, 9.0\n")

 
        file_id.close()

        sww2csv_gauges(sww.filename, 
                       points_file,
                       verbose=False,
                       use_cache=False,
                       output_centroids=True)

        point1_answers_array = [[0.0,0.0,1.0,3.0,-2.0,3.0,4.0], [2.0,2.0/3600.,10.0,12.0,-2.0,3.0,4.0]]
        point1_filename = 'gauge_point1.csv'
        point1_handle = file(point1_filename)
        point1_reader = reader(point1_handle)
        point1_reader.next()

        line=[]
        for i,row in enumerate(point1_reader):
            line.append([float(row[0]),float(row[1]),float(row[2]),float(row[3]),
                         float(row[4]),float(row[5]),float(row[6])])
#           print 'assert line',line[i],'point1',point1_answers_array[i]
            assert num.allclose(line[i], point1_answers_array[i])

        point2_answers_array = [[0.0,0.0,1.0,5.0,-4.0,3.0,4.0], [2.0,2.0/3600.,10.0,14.0,-4.0,3.0,4.0]]
        point2_filename = 'gauge_point2.csv' 
        point2_handle = file(point2_filename)
        point2_reader = reader(point2_handle)
        point2_reader.next()
                        
        line=[]
        for i,row in enumerate(point2_reader):
            line.append([float(row[0]),float(row[1]),float(row[2]),float(row[3]),
                         float(row[4]),float(row[5]),float(row[6])])
#           print i, 'assert line',line[i],'point2',point2_answers_array[i]
            assert num.allclose(line[i], point2_answers_array[i])
                         
        # clean up
        point1_handle.close()
        point2_handle.close()
        os.remove(mesh_file)		
        os.remove(sww.filename)
        os.remove(points_file)
        os.remove(point1_filename)
        os.remove(point2_filename)


    def test_sww2csv_output_centroid_attribute(self):

        def elevation_function(x, y):
            return -x
        
        """Check sww2csv timeseries at centroid, then output the centroid coordinates.
        
        Test the ability to get a timeseries at the centroid of a triangle, rather
		than the given gauge point, then output the results.
        """
        
        # Create rectangular mesh
        mesh_file = tempfile.mktemp(".tsh")    
        points = [[0.0,0.0],[6.0,0.0],[6.0,6.0],[0.0,6.0]]
        m = Mesh()
        m.add_vertices(points)
        m.auto_segment()
        m.generate_mesh(verbose=False)
        m.export_mesh_file(mesh_file)
        
        # Create shallow water domain
        domain = Domain(mesh_file)
        
        domain.default_order=2
        
        # This test was made before tight_slope_limiters were introduced
        # Since were are testing interpolation values this is OK
        domain.tight_slope_limiters = 0 
        

        # Set some field values
        domain.set_quantity('elevation', elevation_function)
        domain.set_quantity('friction', 0.03)

        ######################
        # Boundary conditions
        B = Transmissive_boundary(domain)
        domain.set_boundary( {'exterior': B})

        # This call mangles the stage values.
        domain.distribute_to_vertices_and_edges()
        domain.set_quantity('stage', 1.0)


        domain.set_name('datatest' + str(time.time()))
        domain.smooth = True
        domain.reduction = mean


        sww = SWW_file(domain)
        sww.store_connectivity()
        sww.store_timestep()
        domain.set_quantity('stage', 10.0) # This is automatically limited
        # so it will not be less than the elevation
        domain.time = 2.
        sww.store_timestep()

        # create a csv file containing our gauge points
        points_file = tempfile.mktemp(".csv")
        file_id = open(points_file,"w")
 
# These values are slightly off the centroids - will it find the centroids?
        file_id.write("name, easting, northing, elevation \n\
point1, 2.5, 4.25, 3.0\n")

        file_id.close()

        sww2csv_gauges(sww.filename, 
                       points_file,
                       quantities=['stage', 'xcentroid', 'ycentroid'],
                       verbose=False,
                       use_cache=False,
                       output_centroids=True)

        point1_answers_array = [[0.0,0.0,1.0,4.0,4.0], [2.0,2.0/3600.,10.0,4.0,4.0]]
        point1_filename = 'gauge_point1.csv'
        point1_handle = file(point1_filename)
        point1_reader = reader(point1_handle)
        point1_reader.next()

        line=[]
        for i,row in enumerate(point1_reader):
            line.append([float(row[0]),float(row[1]),float(row[2]),float(row[3]),float(row[4])])
#            print 'assert line',line[i],'point1',point1_answers_array[i]
            assert num.allclose(line[i], point1_answers_array[i])

        # clean up
        point1_handle.close()
        os.remove(mesh_file)		
        os.remove(sww.filename)
        os.remove(points_file)
        os.remove(point1_filename)
		
		

#-------------------------------------------------------------

if __name__ == "__main__":
    suite = unittest.makeSuite(Test_Util, 'test')
#    runner = unittest.TextTestRunner(verbosity=2)
    runner = unittest.TextTestRunner(verbosity=1)
    runner.run(suite)
