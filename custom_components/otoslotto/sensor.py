import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from datetime import timedelta
from datetime import datetime
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME, CONF_API_KEY, CONF_ICON
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

import pandas as pd

REQUIREMENTS = ["pandas==1.2.0"]

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://bet.szerencsejatek.hu/cmsfiles/"
OTOS_NUMBERS_CSV = "otos.csv"

DEFAULT_NAME = "otoslotto"
DEFAULT_ICON = "mdi:clover"

COMM_LOTTO_FORMAT = "{} {} {} {} {}"

MIN_TIME_BETWEEN_SENSOR_UPDATES = timedelta(seconds=21600)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,}
)


def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    name = config.get(CONF_NAME)

    lotto = OtosLottoAPI(name)

    async_add_entities([OtosLottoNumbersSensor(name, lotto)], True)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add a entity from a config_entry."""
    lotto = OtosLottoAPI(DEFAULT_NAME)

    async_add_devices([OtosLottoNumbersSensor(DEFAULT_NAME, lotto)])


class OtosLottoAPI:
    def __init__(self, name):
        """Initialize the OtosLotto API."""
        self._name = name
        self.result = {}

    def update(self):
        """Update function for updating api information."""
        try:
            dt = datetime.now()
            syncDate = dt.strftime("%Y-%m-%d %H:%M:%S")

            url = BASE_URL + OTOS_NUMBERS_CSV
            columns = [
                "year",
                "week",
                "date",
                "no_of_5s",
                "winnings_of_5s",
                "no_of_4s",
                "winnings_of_4s",
                "no_of_3s",
                "winnings_of_3s",
                "no_of_2s",
                "winnings_of_2s",
                "num1",
                "num2",
                "num3",
                "num4",
                "num5",
            ]

            df = pd.read_csv(url, delimiter=";", names=columns)

            # Get latest result
            latest_result = df.loc[0].to_dict()

            lotto_dict = {
                "number_1": int(latest_result["num1"]),
                "number_2": int(latest_result["num2"]),
                "number_3": int(latest_result["num3"]),
                "number_4": int(latest_result["num4"]),
                "number_5": int(latest_result["num5"]),
                "year": int(latest_result["year"]),
                "week": int(latest_result["week"]),
                "lottery_date": latest_result["date"],
                "no_of_5s": int(latest_result["no_of_5s"]),
                "winnings_of_5s": latest_result["winnings_of_5s"],
                "no_of_4s": int(latest_result["no_of_4s"]),
                "winnings_of_4s": latest_result["winnings_of_4s"],
                "no_of_3s": int(latest_result["no_of_3s"]),
                "winnings_of_3s": latest_result["winnings_of_3s"],
                "no_of_2s": int(latest_result["no_of_2s"]),
                "winnings_of_2s": latest_result["winnings_of_2s"],
                "sync_date": syncDate,
            }

            self.result = lotto_dict
        except Exception as ex:
            _LOGGER.error("Failed to update Otos Lotto API status Error: %s", ex)
            raise


class OtosLottoNumbersSensor(Entity):
    def __init__(self, name, api):
        self._name = name
        self._api = api
        self._icon = DEFAULT_ICON
        self._state = None
        self.numbers = {}

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return "sensor.otoslotto"

    @property
    def name(self):
        """Return the name of the sensor, if any."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return COMM_LOTTO_FORMAT.format(
            self.numbers.get("number_1", "-"),
            self.numbers.get("number_2", "-"),
            self.numbers.get("number_3", "-"),
            self.numbers.get("number_4", "-"),
            self.numbers.get("number_5", "-"),
        )

    @Throttle(MIN_TIME_BETWEEN_SENSOR_UPDATES)
    def update(self):
        """Get the latest state of the sensor."""
        if self._api is None:
            return
        # Saturday : 6
        dt = datetime.now()
        nWeekDay = dt.weekday()

        self._api.update()
        lotto_dict = self._api.result

        self.numbers = lotto_dict

    @property
    def device_state_attributes(self):
        """Attributes."""
        return {key: self.numbers[key] for key in sorted(self.numbers.keys())}

    @property
    def device_info(self):
        return {
            "identifiers": {("otoslotto", "sensor.otoslotto")},
            "name": "Otos Lotto 5/90 [HUN]",
            "author": "Gyula Halmos",
        }
