"""
General functions used in fit and interpolate.

   Ole Nielsen, Stephen Roberts, Duncan Gray
   Geoscience Australia, 2006.

"""
from Numeric import dot

from numerical_tools import get_machine_precision

def search_tree_of_vertices(root, mesh, x):
    """
    Find the triangle (element) that the point x is in.
    
    root: A quad tree of the vertices
    Return the associated sigma and k values
    (and if the element was found) .
    """
    #Find triangle containing x:
    element_found = False

    # This will be returned if element_found = False
    sigma2 = -10.0
    sigma0 = -10.0
    sigma1 = -10.0
    k = -10.0
            
    #Find vertices near x
    candidate_vertices = root.search(x[0], x[1])
    is_more_elements = True

    element_found, sigma0, sigma1, sigma2, k = \
                   _search_triangles_of_vertices(mesh,
                                                 candidate_vertices, x)
    while not element_found and is_more_elements:
        candidate_vertices, branch = root.expand_search()
        if branch == []:
            # Searching all the verts from the root cell that haven't
            # been searched.  This is the last try
            element_found, sigma0, sigma1, sigma2, k = \
                           _search_triangles_of_vertices(mesh,
                                                         candidate_vertices, x)
            is_more_elements = False
        else:
            element_found, sigma0, sigma1, sigma2, k = \
                       _search_triangles_of_vertices(mesh,
                                                     candidate_vertices, x)

    return element_found, sigma0, sigma1, sigma2, k

def _search_triangles_of_vertices(mesh, candidate_vertices, x):
    #Find triangle containing x:
    element_found = False

    # This will be returned if element_found = False
    sigma2 = -10.0
    sigma0 = -10.0
    sigma1 = -10.0
    k = -10.0
    #print "*$* candidate_vertices", candidate_vertices
    #For all vertices in same cell as point x
    for v in candidate_vertices:
        #FIXME (DSG-DSG): this catches verts with no triangle.
        #Currently pmesh is producing these.
        #this should be stopped, 
        if mesh.vertexlist[v] is None:
            continue
        #for each triangle id (k) which has v as a vertex
        for k, _ in mesh.vertexlist[v]:
            #Get the three vertex_points of candidate triangle
            xi0 = mesh.get_vertex_coordinate(k, 0)
            xi1 = mesh.get_vertex_coordinate(k, 1)
            xi2 = mesh.get_vertex_coordinate(k, 2)

            #Get the three normals
            n0 = mesh.get_normal(k, 0)
            n1 = mesh.get_normal(k, 1)
            n2 = mesh.get_normal(k, 2)
            
            #Compute interpolation
            sigma2 = dot((x-xi0), n2)/dot((xi2-xi0), n2)
            sigma0 = dot((x-xi1), n0)/dot((xi0-xi1), n0)
            sigma1 = dot((x-xi2), n1)/dot((xi1-xi2), n1)

            # Integrity check - machine precision is too hard, but at
            # least check that we are within a couple of orders of magnitude
            epsilon = get_machine_precision()
            msg = 'abs(sigma0+sigma1+sigma2-1) = %.15e, 100*eps = %.15e'\
                  %(abs(sigma0+sigma1+sigma2-1), 100*epsilon)
            assert abs(sigma0 + sigma1 + sigma2 - 1.0) < 100*epsilon, msg

            #Check that this triangle contains the data point
            
            # Sigmas are allowed to get negative within
            # machine precision on some machines (e.g nautilus)
            if sigma0 >= -epsilon and sigma1 >= -epsilon and sigma2 >= -epsilon:
                element_found = True
                break

        if element_found is True:
            #Don't look for any other triangle
            break
    return element_found, sigma0, sigma1, sigma2, k


