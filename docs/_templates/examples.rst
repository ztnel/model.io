========
Examples
========

This section provides a practical look at software design problems which can be solved using myosin. These examples are derived from real-world software 


Case Study - Telemetric Reporting
---------------------------------

Let's assume we need to create a software service which is required to read telemetry at a regular rate from a plant monitoring microcontroller and update some external software components based on the results of the inbound telemetry payloads. Here is a sample payload from the sensor over a serial interface after unpacking:

.. code-block:: console

    {
        'tp': 40.3,
        'lux': 2344,
        'rh': 56.7,
        'sm': 78,
        'ts': 1652152110,
        'cal': 1652112345
    }

Where:

tp
    is the ambient temperature.

lux
    ambient luminous flux.

rh
    is the ambient relative humidity.

sm
    is the percentage of moisture in the soil.

ts
    is the sensor metric aggregation epoch timestamp.


is the last calibration epoch timestamp.

Let's suppose on any change to `tp`, `lux`, `rh` `sm` and `ts` keys we want to report those changes to an MQTT stream via another cloud interface module. Furthemore, if a change to `cal` is detected we want to send an POST request to our backend to save the new calibration timestamp.

.. code-block:: python3

    class MCUInterface:
        def __init__(self):


    class CloudInterface:

        def report_telemetry

    class ApiInterface:
        def __init__(self):