import yaml


class UploadConfig():
    """
    Config object for GCP upload

    Args:
        configfile_path: filepath to config file
    """

    def __init__(self, configfile_path):
        self.configfile = configfile_path
        self.configs = self.parse_config()
        self.dlp_configs = self.parse_dlp_config()
        self.info_types = self.parse_info_types()
        self.project_name = self.parse_project_name()
        self.key_file = self.parse_key_file()
        self.kms_key = self.parse_kms_key()

    def parse_config(self):
        """
        Parse YAML config file

        Returns:
        """
        with open(self.configfile) as file:
            configs = yaml.load(file, Loader=yaml.FullLoader)
        return configs

    def parse_dlp_config(self):
        """
        Parse configs attribute for dlp info

        Returns: dict with dlp config info
        """
        if 'dlp' in self.configs.keys():
            return self.configs['dlp']
        else:
            return None

    def parse_kms_key(self):
        """
        Parse configs attribute for KMS info

        Returns: dict with KMS config info
        """
        if 'kms_key' in self.configs.keys():
            return self.configs['kms_key']
        else:
            return None

    def parse_info_types(self):
        """
        Parse info type from config attribute

        Returns:
        """
        if 'dlp' in self.configs.keys():
            for info in self.configs['dlp'].keys():
                if info == 'info_types':
                    return self.configs['dlp'][info]
        else:
            return None

    def parse_project_name(self):
        """
        Parse project name from config attribute

        Returns:
        """
        if 'project_name' in self.configs.keys():
            return self.configs['project_name']
        else:
            return None

    def parse_key_file(self):
        """
        Parse key file from config attribute

        Returns:

        """
        if 'key_file' in self.configs.keys():
            return self.configs['key_file']
        else:
            return None

    def get_configs(self):
        """
        Returns:

        """
        return self.configs

    def get_dlp_configs(self):
        """
        Returns:

        """
        return self.dlp_configs

    def get_kms_key(self):

        return self.kms_key

    def get_info_types(self):
        """
        Returns:

        """
        return self.info_types

    def get_project_name(self):
        """
        Returns:

        """
        return self.project_name

    def get_key_file(self):
        """
        Returns:

        """
        return self.key_file


class BigQueryViewConfig():
    """
    Abstract config object for use when generating Big Query views

    Args:
        configfile_path (str): Filepath for config file
    """

    def __init__(self, configfile_path):

        self.configfile = configfile_path
        self.configs = self.__parse_config()
        self.views = self.__parse_views()

    def __parse_config(self):
        """
        Parse YAML config file

        Returns: Dict containing all config info
        """
        with open(self.configfile) as file:
            configs = yaml.load(file, Loader=yaml.FullLoader)
        return configs

    def __parse_views(self):
        """
        Parse config attribute for views info

        Returns: Dict containing views config info
        """
        if 'views' in self.configs.keys():
            return self.configs['views']
        else:
            return None

    def get_config(self):
        """
        Returns: Dict containing all config info
        """
        return self.configs

    def get_views(self):
        """
        Returns: Dict containing views config info
        """
        return self.views


class SubmissionConfig():
    """
    Config object for pipeline submissions

    Args:
        configfile_path: filepath to config file
    """

    def __init__(self, configfile_path):
        self.configfile = configfile_path
        self.configs = self.parse_config()
        self.submissions = self.parse_submissions()

    def parse_config(self):
        """
        Parse YAML config file

        Returns:
        """
        with open(self.configfile) as file:
            configs = yaml.load(file, Loader=yaml.FullLoader)
        return configs

    def parse_submissions(self):
        """
        Parse submissions in YAML config

        """
        if 'submissions' in self.configs.keys():
            return self.configs['submissions']
        else:
            return None

    def get_submissions(self):
        """
        Get submissions from config
        """
        return self.submissions


class LoadConfig():

    def __init__(self, configfile_path):
        self.configfile = configfile_path
        self.configs = self.parse_config()
        self.key_file = self.parse_key_file()
        self.project_id = self.parse_project_id()
        self.sources = self.parse_sources()
        self.destination = self.parse_destination()
        self.destination_project_id = self.parse_project_id()
        self.destination_dataset = self.parse_dataset()
        self.destination_table = self.parse_table()
        self.destination_schema = self.parse_schema()
        self.destination_features = self.parse_features()
        self.mode = self.parse_mode()

    def parse_config(self):
        """
        Parse YAML config file

        Returns:
        """
        with open(self.configfile) as file:
            configs = yaml.load(file, Loader=yaml.FullLoader)
        return configs

    def parse_key_file(self):
        """
        Parse key file in YAML config file

        Returns:
        """
        if 'key_file' in self.configs.keys():
            return self.configs['key_file']
        else:
            return None

    def parse_project_id(self):
        """
        Parse project ID in YAML config

        """
        if 'project_id' in self.configs.keys():
            return self.configs['project_id']
        else:
            return None

    def parse_sources(self):
        """
        Parse submissions in YAML config

        """
        if 'sources' in self.configs.keys():
            return list(self.configs['sources'].values())
        else:
            return None

    def parse_destination(self):
        """
        Parse submissions in YAML config

        """
        if 'destination' in self.configs.keys():
            return self.configs['destination']
        else:
            return None

    def parse_dataset(self):
        """
        Parse submissions in YAML config

        """
        if 'dataset' in self.destination.keys():
            return self.destination['dataset']
        else:
            return None

    def parse_table(self):
        """
        Parse submissions in YAML config

        """
        if 'table' in self.destination.keys():
            return self.destination['table']
        else:
            return None

    def parse_schema(self):
        """
        Parse submissions in YAML config

        """
        if 'schema' in self.destination.keys():
            return self.destination['schema']
        else:
            return None

    def parse_features(self):
        """
        Parse submissions in YAML config

        """
        if 'features' in self.destination.keys():
            return self.destination['features']
        else:
            return None

    def parse_mode(self):
        """
        Parse submissions in YAML config

        """
        if 'mode' in self.destination.keys():
            return self.destination['mode']
        else:
            return None


class FeatureEngineeringFunction():
    """
    Abstract base config object for use when generating feature engineering objects
    """

    def __init__(self, configfile_path):
        self.configfile = configfile_path
        self.configs = self.__parse_config()
        self.project_id = self.parse_project_id()
        self.key_file = self.parse_key_file()
        self.source_dataset = self.parse_source_dataset()
        self.source_table = self.parse_source_table()
        self.destination_dataset = self.parse_destination_dataset()
        self.destination_table = self.parse_destination_table()
        self.staging_bucket = self.parse_staging_bucket()
        self.engineered_features = self.parse_engineered_features()

    def __parse_config(self):
        """
        Parse YAML config file

        Returns: Dict containing all config info
        """
        with open(self.configfile) as file:
            configs = yaml.load(file, Loader=yaml.FullLoader)
        return configs

    def get_config(self):
        """
        Returns: Dict containing all config info
        """
        return self.configs

    def parse_project_id(self):
        """
        Parse project ID in YAML config

        """
        if 'project_id' in self.configs.keys():
            return self.configs['project_id']
        else:
            return None

    def parse_key_file(self):
        """
        Parse key file in YAML config file

        Returns:
        """
        if 'key_file' in self.configs.keys():
            return self.configs['key_file']
        else:
            return None

    def parse_source_dataset(self):
        """
        Parse source dataset in YAML config

        """
        if 'source_dataset' in self.configs.keys():
            return self.configs['source_dataset']
        else:
            return None

    def parse_source_table(self):
        """
        Parse source table in YAML config

        """
        if 'source_table' in self.configs.keys():
            return self.configs['source_table']
        else:
            return None

    def parse_destination_dataset(self):
        """
        Parse destination_dataset in YAML config

        """
        if 'destination_dataset' in self.configs.keys():
            return self.configs['destination_dataset']
        else:
            return None

    def parse_destination_table(self):
        """
        Parse destination_table in YAML config

        """
        if 'destination_table' in self.configs.keys():
            return self.configs['destination_table']
        else:
            return None

    def parse_staging_bucket(self):
        """
        Parse staging bucket in YAML config

        """
        if 'staging_bucket' in self.configs.keys():
            return self.configs['staging_bucket']
        else:
            return None

    def parse_engineered_features(self):
        """ parse engineered features
        """
        if 'engineered_features' in self.configs.keys():
            return self.configs['engineered_features']
        else:
            return None


class FeatureEngineeringConfig(FeatureEngineeringFunction):
    """
    Abstract config object for use when generating Big Query views

    Args:
        configfile_path (str): Filepath for config file
    """

    def __init__(self, configfile_path):
        super().__init__(configfile_path)
        self.engineered_features = self.__parse_engineered_features()

    def __parse_engineered_features(self):
        """
        Returns: dictionary of engineered feature properties
        """
        if self.engineered_features is not None:
            for feature in self.engineered_features:
                parameters = dict()
                if "parameters" in self.engineered_features[feature].keys():
                    for para in self.engineered_features[feature]["parameters"]:
                        parameters.update({self.engineered_features[feature]["parameters"][para]["name"]: \
                                               self.engineered_features[feature]["parameters"][para]["value"]})
                    self.engineered_features[feature]["parameters"] = parameters
        return self.engineered_features
