# Standard imports
from datetime import datetime
import json
from pathlib import Path

# Third-party imports
from netCDF4 import Dataset

class PriorStore:
    """A class that contains data and operations to create a NetCDF file that
    that stores specific priors to be overwritten in the SoS.

    Attributes
    ----------
    author: str
        Author of the priors that were generated
    email: str 
        Email address of the author
    output_dir: Path
        Path to where the NetCDF file should be written
    priors_dict: dict
        Dictionary of required prior data
    sos_file: str
        Name of SoS file that contains priors to overwrite
    NODE_LIST: list
        List of variables stored on the num_node dimensio
    MONTHS_LIST: list
        List of variables stored on the num_months dimension
    DAYS_LIST: list
        List of variables stored on the num_days dimension
    PROB_LIST: list
        List of variables stored on the probability dimension

    Methods
    -------
    load_priors(json_file)
        Reads JSON file to populate priors_dict attribute
    create_netcdf()
        Creates a NetCDF file from priors_dict attribute
    """

    NODE_LIST = ["river_type", "logA0_hat", "logn_hat", "b_hat", "logWb_hat", "logDb_hat", "logr_hat", "logA0_sd", "logn_sd", "b_sd", "logWb_sd", "logDb_sd", "logr_sd", "sigma_man", "sigma_amhg"]
    MONTHS_LIST = ["monthly_q"]
    DAYS_LIST =  ["grdc_q", "usgs_q"]
    PROB_LIST = ["flow_duration_q"]

    def __init__(self, author, email, sos_file, output_dir):
        """
        Parameters
        ----------
        author: str
            Author of the priors that were generated
        email: str 
            Email address of the author
        sos_file: str
            Name of SoS file that contains priors to overwrite
        output_dir: Path
            Path to where the NetCDF file should be written
        """

        self.author = author
        self.email = email
        self.priors_dict = None
        self.sos_file = sos_file
        self.output_dir = output_dir

    def load_priors(self, json_file):
        """Reads JSON file to populate priors_dict attribute.
        
        Parameters
        ----------
        json_file: Path
            Path to JSON file
        """

        with open(json_file, 'r') as jf:
            self.priors_dict = json.load(jf)

    def create_netcdf(self):
        """Creates a NetCDF file from priors_dict attribute. 
        
        The resulting file can be emailed to request the overwrite operation.
        """

        # NetCDF file and global attributes
        file_name = self.output_dir / f"{author.replace(' ', '_').lower()}_{self.sos_file.split('_')[0]}.nc"
        ds = Dataset(file_name, 'w')
        ds.author = self.author
        ds.contact = self.email
        ds.sos_file = self.sos_file
        ds.production_date = datetime.now().strftime('%d-%b-%Y %H:%M:%S')

        # Groups
        for source in self.priors_dict.keys():
            # Check if the group has data
            if self.priors_dict[source]:
                # Create groups for each prior and populate with data
                for prior, data in self.priors_dict[source].items():
                    # Group
                    g = ds.createGroup(f"{source}_{prior}")

                    # Attribute
                    g.run_type = data["run_type"]

                    # Dimensions
                    if "reach_ids" in data.keys(): 
                        self.create_dimensions(source, g, num_reaches=len(data["reach_ids"]))
                    else:
                        self.create_dimensions(source, g, num_nodes=len(data["node_ids"]))

                    # Variables
                    self.create_variables(source, prior, data, g)

        # Close dataset file
        ds.close()

    def create_dimensions(self, source, ds, num_reaches=None, num_nodes=None):
        """Create the netCDF dimensions for the group.

        source: str
            Name of source to determine what dimensions to create
        ds: netCDF4.Dataset
            Dataset to create dimension in
        num_reaches: int
            Number of reaches included in priors data
        num_nodes: int
            Number of nodes included in priors data
        """

        if num_reaches: ds.createDimension("num_reaches", num_reaches)
        if num_nodes: ds.createDimension("num_nodes", num_nodes)

        if source == "wbm" or source == "grades" or source == "grdc" or source == "usgs":
            # Months
            ds.createDimension("num_months", 12)

            # Probability values for flow duration curve
            ds.createDimension("probability", 20)

        if source == "grdc":
            # Number of days
            ds.createDimension("num_days", None)

        if source == "usgs":
            # Number of days
            ds.createDimension("num_days", None)
            # Character units for USGS identifier
            ds.createDimension("nchars", 16)

    def create_variables(self, source, prior, data, ds):
        """Create and populate NetCDF variables.
        
        Parameters
        ----------
        source: str
            Name of data source
        prior: str
            Name of prior
        data: dict
            Dictionary of variables to create and populate
        ds: netCDF4.Dataset
            Dataset to create variables in
        """

        # Store variable-length data
        if source == "gbnode" and prior in self.NODE_LIST:
            node_id = ds.createVariable("node_id", "i8", ("num_nodes",))
            node_id[:] = data["node_ids"]

            indexes = ds.createVariable("indexes", "i4", ("num_nodes",))
            indexes[:] = data["indexes"]

            values = ds.createVariable("prior_values", data["data_type"], ("num_nodes",))
            values[:] = data["values"]

        elif prior in self.PROB_LIST:
            reach_id = ds.createVariable("reach_id", "i8", ("num_reaches",))
            reach_id[:] = data["reach_ids"]

            indexes = ds.createVariable("indexes", "i4", ("num_reaches",))
            indexes[:] = data["indexes"]

            values = ds.createVariable("prior_values", data["data_type"], ("num_reaches", "probability"))
            values[:] = data["values"]

        elif prior in self.MONTHS_LIST:
            reach_id = ds.createVariable("reach_id", "i8", ("num_reaches",))
            reach_id[:] = data["reach_ids"]

            indexes = ds.createVariable("indexes", "i4", ("num_reaches",))
            indexes[:] = data["indexes"]

            values = ds.createVariable("prior_values", data["data_type"], ("num_reaches", "num_months"))
            values[:] = data["values"]

        elif prior in self.DAYS_LIST:
            reach_id = ds.createVariable("reach_id", "i8", ("num_reaches",))
            reach_id[:] = data["reach_ids"]

            indexes = ds.createVariable("indexes", "i4", ("num_reaches",))
            indexes[:] = data["indexes"]

            values = ds.createVariable("prior_values", data["data_type"], ("num_reaches", "num_days"))
            values[:] = data["values"]

            value_t = ds.createVariable("value_t", "f8", ("num_reaches", "num_days"))
            value_t[:] = data["value_t"]

        else:
            reach_id = ds.createVariable("reach_id", "i8", ("num_reaches",))
            reach_id[:] = data["reach_ids"]

            indexes = ds.createVariable("indexes", "i4", ("num_reaches",))
            indexes[:] = data["indexes"]

            values = ds.createVariable("prior_values", data["data_type"], ("num_reaches",))
            values[:] = data["values"]


if __name__ == "__main__":

    # Required data
    author = ""    # Your name
    email = ""    # Your email address
    sos_file = ""    # Just the file name (no Path)
    json_file = Path("")    # Path to the JSON file with priors data
    output_dir = Path("")    # Path where you would like the NetCDF file written to

    # Run Operartions to create NetCDF
    store = PriorStore(author, email, sos_file, output_dir)
    store.load_priors(json_file)
    store.create_netcdf()