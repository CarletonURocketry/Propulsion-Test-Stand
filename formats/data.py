"""
Data format example for data sent from the teststand to the control side. Structure is defined by config.toml file, both config files should be kept in sync.
"""
{
"type": "data", # Type of message, should always be "data
"content": {
"time": {
    "elapsedTime": float, # Elapsed time in seconds with decimal seconds allowed
    "currentTime": float # Time on the server, as a unix time stamp with decimal seconds allowed
},
"valves": {
    "xv1": bool,
    "xv2": bool,
    "xv3": bool,
    "xv4": bool,
    "xv5": bool,
    "xv6": bool
    },
"pressures": { # Pressure Readings
    "pi1": float,
    "pi2": float
},
"temps": { # Temperature Readings
    "t1": float,
    "t2": float
},
"loads": { # Load Cell and strain gauge readings
    "tankMass": float, # Reading from strain gauge
    "thrust": float # Reading from load cell
}
}
} # type: ignore