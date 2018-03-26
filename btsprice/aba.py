# -*- coding: utf-8 -*-
import datetime
import time
import math

ABA = ["HERTZ", "HERO"]

SECONDS_PER_DAY = 60 * 60 * 24

def _get_hertz_feed(reference_timestamp, current_timestamp, period_days, phase_days, reference_asset_value, amplitude):
    """
    Given the reference timestamp, the current timestamp, the period (in days), the phase (in days), the reference asset value (ie 1.00) and the amplitude (> 0 && < 1), output the current hertz value.
    You can use this formula for an alternative HERTZ asset!
    Be aware though that extreme values for amplitude|period will create high volatility which could cause black swan events. BSIP 18 should help, but best tread carefully!
    """
    hz_reference_timestamp = datetime.datetime.strptime(reference_timestamp, "%Y-%m-%dT%H:%M:%S").timestamp() # Retrieving the Bitshares2.0 genesis block timestamp
    hz_period = SECONDS_PER_DAY * period_days
    hz_phase = SECONDS_PER_DAY * phase_days
    hz_waveform = math.sin(((((current_timestamp - (hz_reference_timestamp + hz_phase))/hz_period) % 1) * hz_period) * ((2*math.pi)/hz_period)) # Only change for an alternative HERTZ ABA.
    hz_value = reference_asset_value + ((amplitude * reference_asset_value) * hz_waveform)

    return hz_value

def compute_hertz():
    hertz_reference_timestamp = "2015-10-13T14:12:24" # Bitshares 2.0 genesis block timestamp
    hertz_current_timestamp = datetime.datetime.now() # Current timestamp for reference within the hertz script
    hertz_amplitude = 0.14 # 14% fluctuating the price feed $+-0.14 (2% per day)
    hertz_period_days = 28 # Aka wavelength, time for one full SIN wave cycle.
    hertz_phase_days = 0.908056 # Time offset from genesis till the first wednesday, to set wednesday as the primary Hz day.
    hertz_reference_asset_value = 1.00 # $1.00 USD, not much point changing as the ratio will be the same.

    hz_value = _get_hertz_feed(hertz_reference_timestamp, hertz_current_timestamp.timestamp(), hertz_period_days, hertz_phase_days, hertz_reference_asset_value, hertz_amplitude)

    return hz_value

def compute_hero():
    hero_reference_timestamp = datetime.date(1913, 12, 23)
    current_timestamp = datetime.date.today()
    hero_days_in_year = 365.2425
    hero_inflation_rate = 1.05

    hero_value = hero_inflation_rate ** ((current_timestamp - hero_reference_timestamp).days / hero_days_in_year)

    return hero_value

