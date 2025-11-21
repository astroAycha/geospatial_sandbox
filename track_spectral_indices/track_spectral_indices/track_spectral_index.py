
""" Time eeries for the spectral indecies of Sentinel2 data"""
import openeo
from datetime import datetime, timedelta
import logging
import os

logging.basicConfig(level=logging.INFO)

class TrackSpecIndex:
    """
    Track the change in spectral index over time 
    using relevant spectral indices
    """

    def __init__(self):
        
        # set the connection url
        url = "openeo.dataspace.copernicus.eu/openeo/1.2"
        self.url = url       

    def define_region(self, west, south, east, north):
        """ create a bounding box for the AOI
        expects coordinates
        eg: 95.5, 40.1 etc
        """

        spatial_extent = {"west": west,
                          "south": south,
                          "east": east,
                          "north": north}
        
        return spatial_extent
    

    def temporal_extent(self, start_year, start_month, start_day, 
                              end_year, end_month, end_day, 
                              day_step):
        """
        return the temporal intervals
        for now this works on the full year range
        """

        start_date = datetime(start_year, start_month, start_day)
        end_date = datetime(end_year, end_month, end_day)
        step = timedelta(days=day_step)
        
        dates = []
        current = start_date
        while current <= end_date:
            dates.append(current)
            current += step # 10 days
        
        temporal_intervals = []
        for ds, de in zip(dates[:-1], dates[1:]):
            temporal_intervals.append([ds.strftime("%Y-%m-%d"), 
                                    de.strftime("%Y-%m-%d")])
        
        return temporal_intervals


    def establish_connection(self):
        """establish an authenticated connection"""
        
        connection = openeo.connect(self.url).authenticate_oidc()

        return connection
    

    def create_cube(self, start_year, start_month, start_day,
                          end_year, end_month, end_day,
                          day_step,
                          west, south, east, north):

        temporal_ext = self.temporal_extent(start_year, 
                                            start_month, 
                                            start_day, 
                                            end_year, 
                                            end_month,
                                            end_day,
                                            day_step)
        spatial_ext = self.define_region(west, south, east, north)

        logging.info(f"Fetching data for {spatial_ext}")
        logging.info(f"Fetching data for the period {temporal_ext[0][0], 
                                                     temporal_ext[-1][-1]}")
        
        # establish connection
        eo_connection = self.establish_connection()
        
        for t in temporal_ext:
            logging.info(f"Creating datacube for {t}")

            cube = eo_connection.load_collection('SENTINEL2_L2A',
                                             spatial_extent=spatial_ext,
                                             temporal_extent=t,
                                             bands=["B02", "B04", "B08"])
            logging.info(f"{cube.to_json(indent=None)}")

            blue = cube.band("B02") * 0.0001
            red = cube.band("B04") * 0.0001
            nir = cube.band("B08") * 0.0001
            evi = 2.5 * (nir - red) / (nir + 6.0 * red - 7.5 * blue + 1.0)

            
            # scl_cube = eo_connection.load_collection('SENTINEL2_L2A',
            #                                  spatial_extent=spatial_ext,
            #                                  temporal_extent=t,
            #                                  bands=["SCL"])
            
            # logging.info(f"{scl_cube.to_json(indent=None)}")


            job = evi.create_job(title=f"EVI_{t[0]}", 
                                out_format='NetCDF')
            
            job.start_and_wait()

            # save the output to the Data dir
            # create one if it does not exist
            save_path = './Data/'
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            
            file_name = f'evi_{t[0]}.nc'
            results_file = os.path.join(save_path, file_name)

            # download the results file
            job.download_result(results_file)

    