# -*- coding: utf-8 -*-

# FLEDGE_BEGIN
# See: http://fledge.readthedocs.io/
# FLEDGE_END

""" Plugin for a BME680 temperature and humidity sensor attached directly to the GPIO pins of a Raspberry Pi. """

from datetime import datetime, timezone
import copy
import logging

import adafruit_bme680
import board

from fledge.common import logger
from fledge.plugins.common import utils
from fledge.services.south import exceptions


__author__ = "Willem Remie"
__copyright__ = ""
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'BME680 South Plugin',
        'type': 'string',
        'default': 'bme680',
        'readonly': 'true'
    },
    'assetName': {
        'description': 'Asset name',
        'type': 'string',
        'default': "bme680",
        'order': "1",
        'displayName': 'Asset Name',
        'mandatory': 'true'
    }
}


_LOGGER = logger.setup(__name__)
""" Setup the access to the logging system of Fledge """
_LOGGER.setLevel(logging.INFO)

def plugin_info():
    """ Returns information about the plugin.

    Args:
    Returns:
        dict: plugin information
    Raises:
    """

    return {
        'name': 'BME680 GPIO',
        'version': '1.0.0',
        'mode': 'poll',
        'type': 'south',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(config):
    """ Initialise the plugin.

    Args:
        config: JSON configuration document for the plugin configuration category
    Returns:
        handle: JSON object to be used in future calls to the plugin
    Raises:
    """

    handle = copy.deepcopy(config)
    i2c = board.I2C()
    bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)
    handle["bme680"] = bme680
    return handle


def plugin_poll(handle):
    """ Extracts data from the sensor and returns it in a JSON document as a Python dict.

    Available for poll mode only.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
        returns a sensor reading in a JSON document, as a Python dict, if it is available
        None - If no reading is available
    Raises:
        DataRetrievalError
    """

    try:
        bme680 = handle["bme680"]
        temperature = bme680.temperature
        gas = bme680.gas
        relative_humidity = bme680.relative_humidity
        pressure = bme680.pressure
        altitude = bme680.altitude

        if relative_humidity is not None and temperature is not None:
            time_stamp = utils.local_timestamp()
            readings = {'temperature': temperature, 'relative_humidity': relative_humidity}
            wrapper = {
                    'asset':     handle['assetName']['value'],
                    'timestamp': time_stamp,
                    'readings':  readings
            }
        else:
            raise exceptions.DataRetrievalError
    except Exception:
        raise
    else:
        return wrapper


def plugin_reconfigure(handle, new_config):
    """ Reconfigures the plugin, it should be called when the configuration of the plugin is changed during the
        operation of the south service.
        The new configuration category should be passed.

    Args:
        handle: handle returned by the plugin initialisation call
        new_config: JSON object representing the new configuration category for the category
    Returns:
        new_handle: new handle to be used in the future calls
    Raises:
    """
    _LOGGER.info("Old config for BME680 plugin {} \n new config {}".format(handle, new_config))

    new_handle = copy.deepcopy(new_config)
    return new_handle


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup, to be called prior to the service being shut down.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    Raises:
    """
    _LOGGER.info("BME680 Poll plugin shutdown")