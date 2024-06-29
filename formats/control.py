"""
Data format example for commands sent from the control side to the teststand.
"""
{
"type": "control", # Type of message
"content": {
"valve": {
    "xv1": bool,
    "xv2": bool,
    "xv3": bool,
    "xv4": bool,
    "xv5": bool,
    "xv6": bool
    },
"commands": {
    "fire": bool, # Fire valve servo
    "disconnect": bool # Hose disconnect servo
    }
}
} # type: ignore