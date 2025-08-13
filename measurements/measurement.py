import os
import time
import getpass
import socket
import glob
import logging
import platform
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import devices
from utils.tools import add_coloring_to_emit_ansi


def mkdir(d):
    if not os.path.exists(d):
        os.makedirs(d)


class measurement(object):
    """ Abstract measurement class. """

    def __init__(self, dire="", config=None, current_dose=None, n_annealing=None):
        self.base = dire
        self.config = config or {}

        preexisting_dose = self.config['sample']['preexisting_dose']

        # summing the dose that is supplied by obelix with the preexisting dose. 
        self.current_dose = (current_dose or 0) + preexisting_dose
        # current_dose = self.current_dose #remove this dependency 

        # 2. Construct ID base
        self.id = f"{config['sample']['type']}_{config['sample']['id']}_{self.current_dose}kGy"

        # 3. Append annealing info if applicable
        if "annealing" in config and n_annealing is not None:
            period = config["annealing"].get("period", "X")
            self.id += f"_annealStep{n_annealing}_p{period}min"

        # --- Directory setup ---
        self.ldir = f"{self.base}logs/{self.id}"
        mkdir(self.ldir)

        self.nrun = self.get_run_id(self.id)
        self.rdir = f"{self.ldir}/{self.nrun}"
        mkdir(self.rdir)

        self.logfile = f"{self.rdir}/log.txt"

        # --- Logger setup ---
        logFormatter = logging.Formatter(fmt="[%(asctime)s] [%(levelname)-5.5s]  %(message)s", datefmt='%H:%M:%S')
        self.logging = logging.getLogger('root')
        self.logging.setLevel(logging.DEBUG)

        if not self.logging.handlers:
            if platform.system() != 'Windows':
                logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)

            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logFormatter)
            self.logging.addHandler(consoleHandler)

            fileHandler = logging.FileHandler(filename=self.logfile)
            fileHandler.setFormatter(logFormatter)
            self.logging.addHandler(fileHandler)

        # --- Log header ---
        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("Running test: %s" % self.__class__.__name__)
        self.logging.info("------------------------------------------")
        self.logging.info("\t")


        
    def _initialise_devices(self):
        """
        Dynamically initializes all devices listed in the config file.

        This function iterates through the 'devices' section of the provided
        config, instantiates the corresponding device class with its
        parameters, and attaches it as an attribute to the measurement instance.
        """
        self.logging.info("--- Initialising devices from config ---")
        if 'devices' not in self.config:
            self.logging.warning("No 'devices' section found in the config file.")
            return

        for device_name, params in self.config['devices'].items():
            if device_name =="multimeter": # since the multimeter is only used for the PT1000, we shouldn't initialize it here to avoid conflicts
                continue
            try:
                model_name = params['model']
                # Copy params to pass as keyword arguments, removing 'model'
                init_params = params.copy()
                del init_params['model']

                # Get the class from the 'devices' module
                device_class = getattr(devices, model_name)

                # Instantiate the class with its parameters
                device_instance = device_class(**init_params)

                # Attach the instance to self (e.g., self.sourcemeter_1 = <ke2410 object>)
                setattr(self, device_name, device_instance)
                self.logging.info(f"Successfully initialised '{device_name}' (Model: {model_name})")

            except AttributeError:
                self.logging.error(f"Device model '{model_name}' not found in the devices module.")
            except KeyError:
                self.logging.error(f"Device '{device_name}' is missing the 'model' key in the config.")
            except Exception as e:
                self.logging.error(f"Failed to initialise device '{device_name}': {e}")
        self.logging.info("------------------------------------")
        
    def get_time(self):
        return time.strftime("%H:%M:%S", time.localtime())

    def get_date_time(self):
        return time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())

    def get_user_name(self):
        return getpass.getuser()

    def get_host_name(self):
        return socket.gethostname()

    def get_run_id(self, die_name):
        id_list = [-1]
        for dname in glob.glob("logs/%s/*" % die_name):
            name = os.path.basename(dname)
            if len(name.split("_")) == 3:
                i = int(name.split("_")[0])
                id_list.append(i)
        new_id = max(id_list) + 1
        now = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        run_id = "%02d_%s" % (new_id, now)
        return run_id

    def save_list(self, out, fn="out.dat", info="Saving output to file %s", fmt="%d", header='# Header'):
        np.savetxt('%s/%s' % (self.rdir, fn), np.array(out), fmt, delimiter='\t',  header=header)
        self.logging.info(info % self.rdir+'/'+fn)
        return 0

    def print_graph(self, x, y, yerr, xlabel, ylabel, title, fn="out.dat", info="Saving output to file %s"):
        self.init_style_old()
        #plt.gca().margins(0.1, 0.1)
        plt.errorbar(x, y, yerr=yerr, ls=' ', marker='s')
        plt.gca().yaxis.set_major_formatter(mtick.FormatStrFormatter('%.3E'))
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.tight_layout()
        plt.savefig('%s/%s' % (self.rdir, fn), bbox_inches='tight')
        plt.clf()
        self.logging.info(info % self.rdir+'/'+fn)
        return 0

    def init_style_old(self):
        plt.style.use('seaborn-colorblind')
        #plt.style.use('fivethirtyeight')

        ## Figure
        plt.rcParams['figure.figsize'] = (7.5, 5.5)
        plt.rcParams['figure.titlesize'] = 'large'
        plt.rcParams['figure.titleweight'] = 'normal'
        plt.rcParams['figure.facecolor'] = 'w'
        plt.rcParams['figure.edgecolor'] = 'w'

        ## Fonts
        plt.rcParams['font.size'] = 16
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = 'arial'

        ## Axes
        plt.rcParams['axes.linewidth'] = 1.5
        plt.rcParams['axes.titlesize'] = 'large'
        plt.rcParams['axes.labelsize'] = 'medium'
        plt.rcParams['axes.labelweight'] = 'normal'
        plt.rcParams['axes.spines.left'] = True
        plt.rcParams['axes.spines.bottom'] = True
        plt.rcParams['axes.spines.top'] = False
        plt.rcParams['axes.spines.right'] = False
        plt.rcParams['axes.grid'] = False

        ## Grid
        plt.rcParams['grid.color'] = 'k'
        plt.rcParams['grid.linestyle'] = '--'
        plt.rcParams['grid.linewidth'] = 0.8
        plt.rcParams['grid.alpha'] = 0.5                # transparency, between 0.0 and 1.0

        ## Lines
        plt.rcParams['lines.linewidth'] = 1.3
        plt.rcParams['lines.markeredgewidth'] = 1.5
        plt.rcParams['lines.markersize'] = 6

        ## Markers
        plt.rcParams['markers.fillstyle'] = 'none' # full|left|right|bottom|top|none

        ## Ticks
        plt.rcParams['xtick.color'] = 'k'
        plt.rcParams['xtick.labelsize'] = 'small'
        plt.rcParams['ytick.color'] = 'k'
        plt.rcParams['ytick.labelsize'] = 'small'
        plt.rcParams['xtick.minor.visible'] = True
        plt.rcParams['ytick.minor.visible'] = True
        plt.rcParams['xtick.major.size'] = 8
        plt.rcParams['xtick.minor.size'] = 4.5
        plt.rcParams['xtick.major.width'] = 1.3
        plt.rcParams['xtick.minor.width'] = 1.3
        plt.rcParams['ytick.major.size'] = 8
        plt.rcParams['ytick.minor.size'] = 4.5
        plt.rcParams['ytick.major.width'] = 1.3
        plt.rcParams['ytick.minor.width'] = 1.3
        plt.rcParams['xtick.direction'] = 'out'
        plt.rcParams['ytick.direction'] = 'out'

        plt.gca().xaxis.set_ticks_position('bottom')
        plt.gca().yaxis.set_ticks_position('left')

        ## Legend
        plt.rcParams['legend.frameon'] = False
        plt.rcParams['legend.framealpha'] = 0.8
        plt.rcParams['legend.facecolor'] = 'inherit'
        plt.rcParams['legend.fancybox'] = False
        plt.rcParams['legend.shadow'] = False
        plt.rcParams['legend.numpoints'] = 1
        plt.rcParams['legend.scatterpoints'] = 1
        plt.rcParams['legend.markerscale'] = 1.0
        plt.rcParams['legend.fontsize'] = 'small'

        ## Specific
        plt.rcParams['image.cmap'] = 'viridis'
        plt.rcParams['contour.negative_linestyle'] = 'dashed'       # dashed | solid
        plt.rcParams['errorbar.capsize'] = 0                        # length of end cap on error bars in pixels
        plt.rcParams['savefig.transparent'] = False




    # Prepare
    # ---------------------------------

    def _initialise(self):
        self.logging.info("Start date          : %s" % self.get_date_time())
        self.logging.info("User                : %s" % self.get_user_name())
        self.logging.info("Host                : %s" % self.get_host_name())
        self.logging.info("Identifier          : %s" % self.id)
        self.logging.info("Log will be stored to %s" % self.logfile)
        self.logging.info("\t")

    def _finalise(self):
        plt.close('all') # ensuring plots are closed at the end of every individual measurement session. 
        self.logging.info("\t")
        self.logging.info("Cleaning up.")
        self.logging.info("\t")
        self.logging.info("\t")
