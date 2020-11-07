# Visualization-Analyzation-Tool-for-Biomedical-Researchers
## Contributors:
* Shelden Shi
* Tony Wurt
* Isabella Lee-Rubio
### Installation and setup

This repository requires Python 3.6 (other versions where not tested).

1. Clone and `cd` into repository via: 

   `git clone https://github.com/e-tony/CalHacksProject && cd CalHacksProject`

2. Create a virtual environment for Python via: 

   `python3 -m venv venv`

3. Activate the virtual environment: 

   `source venv/bin/activate`

4. Install the required packages via: 

   ```bash
   pip install --upgrade pip setuptools
   pip install -r requirements.txt
   ```

5. Download the CORD-19 dataset either manually [here](https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge) or download it via the Kaggle API:

   1. Generate a Kaggle API credentials file via `Create API Token` under the `Account` tab on Kaggle.

   2. Move the `kaggle.json` file to `/home/user/.kaggle/`

   3. For security, change read access rights: 

      `chmod 600 ~/.kaggle/kaggle.json` 

   4. Download the CORD-19 dataset via (21 GB):

      `./download_data.sh`

### Running the script

Note: the pretrained models that will be download (specified in `config.yaml`) require about 1 GB of free space.

6a. Execute the following command (adjust the path to the dataset): 

`python main.py --data-dir /path/to/CORD_19_RC/ >> log_1.txt`

6b. Alternatively, you can also run the script in the background via:

`nohup python main.py --data-dir /path/to/CORD_19_RC/ >> log_1.txt &`

You can check if the script is still running by running `htop` or you can check if the script crashed because of an error by opening the log file.
