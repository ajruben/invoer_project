from main import Geopackage
from osgeo import ogr
import time
import numpy as np
import pandas as pd
import os

class GeopackageToINV(Geopackage):
    """
    This class is for retrieving data from a geopackage and convert to a INV (invoer) format for the rekenhart (rh).
    This class inherits from geopackage class, but create is set to false, only want to communicate with an existing geopackage, not generate one.
    """

    def __init__(self ,geopackage, inv_file_location):
        super().__init__(geopackage, create=False) #dont create a new gpkg
        #TODO CHANGE THIS LATER, COMPENSATE FOR CREATE=FALSE, WAS ADDED LATER 
        self.geopackage_name = geopackage
        geopackage = "output\\" + geopackage
        self.geopackage_location = geopackage

        self.inv_file_location = inv_file_location
        self.header = ["Rekenhart NL 1 invoerfile\n","SITUATIE:1\n","VARIANT:00\n","W,Ow2023\n","VERSIE\n\t16\n"] #TODO: GENERATE ONE ACCORDING TO WHAT FITS TO GPKG
    
    #----------------------------------------------------------------------------------------------------
    #methods for writing the invoer file
    def write(self):
        
        print('\nWriting to inv file...\n')
        start_time = time.time()
        self.bebouwing() #cvgg: bouwwerk, rh:bebouwing
        self.wegvakken() #
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"\nFinished writing, time taken: {elapsed_time} seconds.\n")
    
    #----------------------------------------------------------------------------------------------------
    #parameters (in gpkg: field tables, in qgis: layer)
    def bebouwing(self): #cvgg: bouwwerk, rh:bebouwing
        """
        Writing to file. The current method takes about 2 seconds for 100k rows on computer 73, seems to be O(n) time complexity.
        It's 3 times faster than the previous geopandas version for 1k and 100k rows, unknown time complexity.

        Important background on retrieve_coordinates:
        OGR uses tree spatial indexing when creating geometry, which is useful for operations like finding intersections, etc.
        However, we just want to get the coords as floats quickly.
        Retrieving the coordinates in readable format, i.e., floats instead of b"\\xoo(...)", could be done
        using OGR, but it has to loop over every feature, which is SLOW (takes ~30s for ~100k rows).
        Let's use SQLite functionality instead; this is basically instant.
        The table we want for the purpose of getting the float values is rtree_bouwwerk_geom.
        Column info: [(0, 'id', 'INT', 0, None, 0), (1, 'minx', 'REAL', 0, None, 0), (2, 'maxx', 'REAL', 0, None, 0),
                      (3, 'miny', 'REAL', 0, None, 0), (4, 'maxy', 'REAL', 0, None, 0)]
        Also see http://www.geopackage.org/spec120/#extension_rtree section Create Virtual Table.
        But the rows are not in 'id' order (unless you have a certain pattern of geometries, s.a. diagonal),
        but are ordered 'spatially'. Therefore need to order it first. 
        """

        #retrieve and format coord data
        reflectie, index_mapping = self._create_spectrum(layer_name='bouwwerk', spectrum_column = 'band')
        self._retrieve_coordinates_sql(reflectie = reflectie, layer_name = 'bouwwerk')

        temp_file = "inv/" + "temp_invoerfile.txt"
        np.savetxt(temp_file, self.resultaat.astype(float), header="BEBOUWING", fmt='%.2f', delimiter=', ', comments='')
        #oplossing vinden voor sneller formateren #TODO
        with open(temp_file, 'r') as file:
            lines = file.readlines()
            # Modify the values in the lines
            for i in range(len(lines)):
                values = lines[i].split()
                if values[0] == '9999993141592.00,':
                    values[0] = '<0>,'
                    # Remove the last element
                    values = values[:-1]
                    values[-1] = values[-1][:-4] # Remove comma and decimals
                    values[-2] = values[-2][:-4] + ","
                lines[i] = ' '.join(values) + '\n'
            # Open the file for writing and save the changes
            with open(self.inv_file_location, 'w') as file2:
                file2.writelines(lines)
        os.remove(temp_file)

        #creating reflection {tuple(values): (index  + 1000) for index, values in unique}# nog omslachtig, geknoei door <0> toe te voegen. daardoor 25% langzamer. FIXED IT: just edit the newline to include what u want at start of every line.
        reflect_map = {index_mapping[values]: values for values in index_mapping if len(set(values)) != 1}
        reflect_array = [[key, *values] for key, values in reflect_map.items()]
        with open(self.inv_file_location, 'a') as file:
            np.savetxt(file, reflect_array, header="REFLEKTIE", fmt='%d', delimiter=', ', comments='', newline='\n<0>, ') #<---do this, what not to do: follow chatgpt's instructions. it will try to erase the entire file and rewrite it from scratch using forloops, yikes
        file_path = self.inv_file_location

        with open(file_path, 'rb+') as file:
            file.seek(-1, 2)  # Move the cursor to the last character

            while file.read(1) != b'\n':  # Move the cursor backward until a newline character is found
                file.seek(-2, 1)

            file.truncate()  # Truncate the file at the current position

    def wegvakken(self):
        # Uitgangspunt bij het maken van het invoerbestand *.inv is dat de emissie niet wordt meegegeven maar wordt berekend in het RIVM rekenhart
        # Als besloten wordt wel de emissie in de dBvision module te gaan berekenen (bv voor de basisgeluidemissie (BGE)) dan moet dit deel nog worden 
        # aangevuld in het script dat het invoerbestand maakt. 
        EmmissieDag, index_mapping_EmmissieDag = self._create_spectrum(layer_name='wegdeelGPP', spectrum_column = 'emmissieDag')
        EmmissieAvond, index_mapping_EmmissieAvond = self._create_spectrum(layer_name='wegdeelGPP', spectrum_column = 'emmissieAvond')
        EmmissieNacht, index_mapping_EmmissieNacht = self._create_spectrum(layer_name='wegdeelGPP', spectrum_column = 'emmissieNacht')

        




    #----------------------------------------------------------------------------------------------------
    #help methods
    def _create_spectrum(self, layer_name, spectrum_column):
        print(layer_name)
        print(gpkg.column_names('bouwwerk'))
        columns = self.column_names(layer_name)
        #-------reflecties
        contains_spectrum_column = [column_name for column_name in columns if spectrum_column in column_name]
        #print(columns, contains_spectrum_column)
        spectrum_content = self.select_by_column_order(layer_name, order=contains_spectrum_column)
        unique = list(enumerate(set(map(tuple, spectrum_content)))) # Outer things are to format data; set matters: gives back unique values
        
        # Create a dictionary to map each unique tuple to its index
        if layer_name == "bouwwerk":
            index_mapping = {tuple(values): (index  + 1000) for index, values in unique} #reflection indeces have to start from 1000, not sure for others
        elif layer_name == "wegdeelGPP":
            index_mapping = {tuple(values): index + 1 for index, values in unique} #reflection indeces have to start from 1000, not sure for others
        spectrum = [values[0] if len(set(values)) == 1 else index_mapping[tuple(values)] for values in spectrum_content] # if spectrum is constant over all bands, just give reflection, else give spectnr
        return spectrum, index_mapping
        #retrieve and format coord data

    def _retrieve_coordinates_sql(self, reflectie, layer_name): #TODO:
        """
        General comment: tuple comprehensions are mainly used due to speed.

        This way to retrieve coordinate data is the current prefered way, as this queries the geopackage sqlitedatabase directly, which is fast.
        ogr provides a mean to perform spatial queries. 
        by creating your own sql query, you can retrieve the results faster than by looping over the features using the ogr module.
        The result is not directly loaded into memory, it returns and iterator, and as we want to perfor moperations we need to load into memeory by iterating and saving to list.
        this is some ogr object that looks like a string with lots of info we don't need, since we're only interested in the coordinate data.
        Therefore, we convert it to a string, and using str.index() we select the coordinate part of the string.
        the results list thus contains a tuple of coords as a string in the following format:
        (str(x1 y1 z1 m1, x2 y2 z2 m2, ..., x1 y1 z1 m1), ...) -> `...` == for each polygon, until the last polygon
        """
        driver = ogr.GetDriverByName("GPKG")
        geopackage_ds = driver.Open(self.geopackage_location, 1)  
        sql_query = f"SELECT ST_AsText(geom) AS wkt FROM {layer_name}"
        result = geopackage_ds.ExecuteSQL(sql_query)                                                        
        result_gen = (res for res in result)                                                           #result is some ogr object that must be iterated over to obtain the result, kind of like fetchall()
        results_gen = (str(res)[str(res).index("((") + 2 :str(res).index("))\n\n")] for res in result_gen) #get the result in a semi useful format

        """
        Creating tuple as: 
        ((polygon_index, (x1,y1,z1, m1), (x2,y2,z2,m2), ..., (x1,y1,z1, m1)), (poly_index + 1, (x1,y1,z1, m1), (x2,y2,z2,m2), ..., (x1,y1,z1, m1)),
        ...,  (last_poly_index, (x1,y1,z1, m1), (x2,y2,z2,m2), ..., (x1,y1,z1, m1)))
        with polyindexing starting at 1, the coordinate tuples refering to the points that represents the polygon's corners.
        Hence last polyindex denotes number of polygons, and for each polygon the amount of coordinate tuples denote the amount of corners of the polygon.

        It a double loop. The outer loop loops over the elements of results tuple.
        The inner loop deal with converting this string to a tuple of tuples as denoted above for each polygon.

        We keep track of the polygon index in the outer loop and add that to the tuple of tuples created inside the inner loop. (basically creating a new tuple)
        """
        
        polygon_coordinates_gen = ((tuple( map ( float, point.split())) for point in string.split(', ')) for string in results_gen)
        polygon_coordinates_tup = tuple(tuple((poly_index + 1, tuple(coord_tuple for coord_tuple in polygon_gen))) for poly_index, polygon_gen in enumerate(polygon_coordinates_gen))
        
        polygon_corners = tuple(len(polygon_data[1]) for polygon_data in polygon_coordinates_tup) #take into account that index is also counted, so actual number is one less.
        most_corners = max(polygon_corners) 
        corners_needed = tuple(most_corners - corners for corners in polygon_corners)

        from itertools import chain #to unpack tuple
        polygon_padded_tup = [(polygon_data[0],) + tuple(chain(*polygon_data[1])) + (31415, -31415, 31415, -31415) * pad_factor for pad_factor, polygon_data in zip(corners_needed, polygon_coordinates_tup)]
        
        #Convert to arrays for vectorized operations:
        coord_data = np.array(np.array(polygon_padded_tup).tolist())
        
        #Creating headliners    
        combined = np.column_stack((coord_data, reflectie))
        zero_column = np.zeros((coord_data.shape[0], 1))
        prep_combine = np.column_stack((combined, zero_column))
        flag_column = np.repeat(9999993141592, coord_data.shape[0])
        headerline = np.column_stack((flag_column, prep_combine[:, [0, -2, -1]]))
        
        #try create coords part:
        x_mask = [i for i in range(1, len(coord_data[0]), 4)]
        y_mask = [i for i in range(2, len(coord_data[0]), 4)]
        z_mask = [i for i in range(3, len(coord_data[0]), 4)]
        m_mask = [i for i in range(4, len(coord_data[0]), 4)]
        x_columns = coord_data[:,x_mask]
        y_columns = coord_data[:,y_mask]
        z_columns = coord_data[:,z_mask]
        m_columns = coord_data[:,m_mask]

        """
        coord_box is a 3D numpy array, where each `layer/slice` is a matrix (a 2D numpy array), where each matrix is basically a matrix of 4 stacked columns (a 1D numpy array), 
        which represent the coordinates, of one of the polygons.

        example for a matrix of a ZM polygon with 4 vertices:
        [[x1 y1 z1 m1]
        [x2 y2 z2 m2]
        [x3 y3 z3 m3]
        [x4 y4 z4 m4]
        [x1 y1 z1 m1]]

        example of a stacked matrix for two ZM polygons with 4 vertices:
        [
        [[x1 y1 z1 m1]
        [x2 y2 z2 m2]
        [x3 y3 z3 m3]
        [x4 y4 z4 m4]
        [x1 y1 z1 m1]]

        [[x1 y1 z1 m1]
        [x2 y2 z2 m2]
        [x3 y3 z3 m3]
        [x4 y4 z4 m4]
        [x1 y1 z1 m1]]
        ]

        the amount of rows denote the amount of vertices (n_vertices = n_row -1).
        The amount of matrices denote the amount of polygons.
        """
        coord_box = np.dstack((x_columns, y_columns, z_columns, m_columns)) #Stack arrays in sequence depth wise (along third axis).
        headerline_3d = headerline[:, np.newaxis, :]
        result_array = np.concatenate((headerline_3d, coord_box), axis=1)
        flat_matrix = np.reshape(result_array, (result_array.shape[0] * result_array.shape[1], result_array.shape[2]))
        # Reshape coord_box into a 2D matrix
        pattern = np.array([31415, -31415, 31415, -31415])
        matches = np.all(flat_matrix == pattern, axis=1)
        filtered_matrix = flat_matrix[~matches]
        
        # Close the GeoPackage
        geopackage_ds = None
        self.resultaat = filtered_matrix

    def __linewriter(self, lines):
        for line in range(len(lines)): #write the lines
            if line==(len(lines)-1):
                f.write(" " + str(lines[line]))
            elif line == 0:
                f.write(str(lines[line] + ","))
            else:
                f.write(" " + str(lines[line]) + ",")
        f.write("\n")

    geopackage = None


if __name__ == '__main__':
    ntf = 'inv\\invoer1.txt'
    gpkg = "test.gpkg"
    gpkg = GeopackageToINV(geopackage = gpkg, inv_file_location=ntf)
    gpkg.connect()
    gpkg.write()
    gpkg.close()
