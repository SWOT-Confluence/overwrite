# overwrite

overwrite contains two classes:
- store.py: PriorStore. This class serves as a template to store priors in a NetCDF file that the user would like to see overwritten in the SoS.
- overwrite.py: Overwrite. This class takes the NetCDF file generated from the PriorStore class and uses it to overwrite priors in the SoS.

Note: store.py will be used by most to guide how they store priors that will overwrite existing priors in the SoS. So, the following instructions will only address this class.

# installation

1. Clone the repository to your file system.
2. PriorStore is best run with Python virtual environments so install venv and create a virutal environment: https://docs.python.org/3/library/venv.html
3. Activate the virtual environment and use pip to install dependencies: `pip install -r requirements.txt`

# setup

## store.py
`store.py` contains example usage and can be executed. Before executing the file you will need to fill out lines 228-233 to match your specific execution of `store.py`. Or include the data found at those lines in a script of your own.

The following is required:
- author (your name)
- email (you email address)
- sos_file (the name of the SoS file you would like to overwrite with new priors)
- json_file (the JSON file that contains the prior data)
- output_dir (Path to the location on your local file system where you would like to write the NetCDF file)

## priors.json

`data/priors.json` is a sample JSON file with a structure you can follow when generating the priors you would like to overwrite in the SoS. A few things to note:

- Not all priors or groups have been tested so there may be some modifications that are specific to a particular prior.
- The first dimension of `values` should equal the size of `reach_ids` (in other words there is a value for each reach identifier).
- If your data is indexed on num_days then make sure to include the days (see `grdc["grdc_q"]`).
- If your data is indexed on num_nodes then make sure to include the node identifiers (see `gbnode[logr_hat]`).
- If your data is indexed on num_months or probability there is no need to include those dimensions but make sure they are accounted for in the shape/dimensions of `values`.
- `run_type` indicates whether you would like to update the constrained or unconstrained version of the SoS. Please only use the values: "constrained" or "unconstrained". If you would like to update both, use two entries.

# execution

1. Activate your virtual environment.
2. Run `python3 store.py`
3. Output is written to the directory you specified in the store.py file.