"""
Data format for commands sent from the control side to the teststand.
"""
{
"valve": {
    "xv1": bool,
    "xv2": bool # Repeat for all valves in config.toml
    },
"fire": bool, # Fire valve servo
"disconnect": bool # Hose disconnect servo
}