# Standard imports
from pathlib import Path

# Third-party imports
from netCDF4 import Dataset
import numpy as np

class Overwrite:
    """Class that overwrites priors in the SOS that are retrieved from a 
    specifically structured NetCDF file.
    
    Attributes
    ----------
    priors_file: Path
        Path to NetCDF with priors data
    sos_file: Path
        Path to the SoS file that contains priors to be overwritten

    Methods
    -------
    determine_group(source)
        Determine the group the prior is generated for
    locate_sos_file(priors_file)
        Locate the SoS file with priors that will be overwritten
    overwrite()
        Overwrite priors in the SoS file
    retrieve_ids(source, priors_ds, sos_ds)
        Retrieve reach identifiers for priors and from SoS
    """

    def __init__(self, priors_file):
        """
        Parameters
        ----------
        priors_file: Path
            Path to NetCDF with priors data
        """

        self.priors_file = priors_file
        self.sos_file = self.locate_sos_file(priors_file)

    def determine_group(self, source):
        """Determine the group the prior is generated for.
        
        Parameters
        ----------
        source: str
            Data source prior was generated from/for
        """

        if source == "wbm" or source == "grades":
            group = "model"
        elif source == "grdc":
            group = "model/grdc"
        elif source == "gbreach":
            group = "gbpriors/reach"
        elif source == "gbnode":
            group = "gbpriors/node"
        else:
            group = "model/usgs"
        
        return group 

    def locate_sos_file(self, priors_file):
        """Locate the SoS file with priors that will be overwritten.
        
        Parameters
        ----------
        priors_file: Path
            Path to NetCDF with priors data
        """

        ds = Dataset(priors_file, 'r')
        sos_file = ds.sos_file
        ds.close()
        return sos_file

    def overwrite(self, sos_dir):
        """Overwrite priors in the SoS file.
        
        Parameters
        ----------
        sos_dir: Path
            Path to directory that contains the current SoS
        """

        priors_ds = Dataset(self.priors_file, 'r')

        for key in priors_ds.groups.keys():

            # Prior data
            source = key.split('_')[0]
            prior = '_'.join(key.split('_')[1:])
            run_type = priors_ds[key].run_type
            prior_indexes = priors_ds[key]["indexes"][:]
            data = priors_ds[key]["prior_values"][:]
            group = self.determine_group(source)

            # SoS data
            sos_file = sos_dir / run_type / self.sos_file
            sos_ds = Dataset(sos_file, 'a')

            # Test data
            if "reach_id" in priors_ds[key].variables.keys():
                prior_ids, sos_ids = self.retrieve_ids(source, priors_ds[key], sos_ds)
            else:
                prior_ids = priors_ds[key]["node_id"][:]
                sos_ids = sos_ds["nodes"]["node_id"][:]
            sorter = np.argsort(sos_ids)
            test_indexes = sorter[np.searchsorted(sos_ids, prior_ids, sorter=sorter)]

            # Overwrite
            if "value_t" in priors_ds[key].variables.keys():
                prior_t = priors_ds[key]["value_t"][:].astype(int)[0]
                sos_t = sos_ds[group][f"{prior}t"][:].astype(int)[0]
                sorter = np.argsort(sos_t)
                index_t = sorter[np.searchsorted(sos_t, prior_t, sorter=sorter)]
                sos_ds[group][prior][prior_indexes,index_t] = data[0]
                success = np.allclose(data[0], sos_ds[group][prior][:][test_indexes,index_t])
            else:
                sos_ds[group][prior][prior_indexes] = data
                success = np.allclose(data, sos_ds[group][prior][test_indexes])
            
            # Status
            if success:
                if source == "gbreach" or source == "gbnode": source = "gbpriors"
                print(f"{source.upper()}: '{prior}' has been overwritten in the SoS ({run_type}).")
            else:
                if source == "gbreach" or source == "gbnode": source = "gbpriors"
                print(f"FAILURE: {source.upper()}: '{prior}' has NOT been overwritten in the SoS ({run_type}).")

            sos_ds.close()
        priors_ds.close()     

    def retrieve_ids(self, source, priors_ds, sos_ds):
        """Retrieve reach identifiers for priors and from SoS.
        
        Parameters
        ----------
        source: str
            Name of prior source
        priors_ds: netCDF4.Dataset
            Dataset with prior values
        sos_ds: netCDF4.Dataset
            SoS dataset
        """

        if source == "usgs":
            prior_ids = priors_ds["reach_id"][:]
            sos_ids = sos_ds["model"]["usgs"]["usgs_reach_id"][:]
        elif source == "grdc":
            prior_ids = priors_ds["reach_id"][:]
            sos_ids = sos_ds["model"]["grdc"]["grdc_reach_id"][:]
        else:
            prior_ids = priors_ds["reach_id"][:]
            sos_ids = sos_ds["reaches"]["reach_id"][:]

        return prior_ids, sos_ids

if __name__ == "__main__":
    
    priors_file = Path("")
    sos_dir = Path("")

    overwrite = Overwrite(priors_file)
    overwrite.overwrite(sos_dir)