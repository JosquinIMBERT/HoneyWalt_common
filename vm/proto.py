global CONTROL_PORT, VM_COMMANDS, COMMIT_PHASE, RUN_PHASE, DEBUG_PHASE
global CMD_VM_PHASE, CMD_VM_HONEYPOTS, CMD_VM_IPS, CMD_VM_WG_KEYGEN, CMD_VM_WG_DOORS, CMD_VM_WG_UP, CMD_VM_WG_DOWN, CMD_VM_FW_UP, CMD_VM_FW_DOWN, CMD_VM_COMMIT, CMD_VM_SHUTDOWN, CMD_VM_LIVE

CONTROL_PORT = 5555

CMD_VM_PHASE = 1

CMD_VM_HONEYPOTS = 2
CMD_VM_IPS = 3

CMD_VM_WG_KEYGEN = 4
CMD_VM_WG_DOORS = 5
CMD_VM_WG_UP = 6
CMD_VM_WG_DOWN = 7

CMD_VM_FW_UP = 8
CMD_VM_FW_DOWN = 9

CMD_VM_COMMIT = 10
CMD_VM_SHUTDOWN = 11
CMD_VM_LIVE = 12

VM_COMMANDS = {
"CMD_VM_PHASE":CMD_VM_PHASE,
"CMD_VM_HONEYPOTS":CMD_VM_HONEYPOTS,
"CMD_VM_IPS":CMD_VM_IPS,
"CMD_VM_WG_KEYGEN":CMD_VM_WG_KEYGEN,
"CMD_VM_WG_DOORS":CMD_VM_WG_DOORS,
"CMD_VM_WG_UP":CMD_VM_WG_UP,
"CMD_VM_WG_DOWN":CMD_VM_WG_DOWN,
"CMD_VM_FW_UP":CMD_VM_FW_UP,
"CMD_VM_FW_DOWN":CMD_VM_FW_DOWN,
"CMD_VM_COMMIT":CMD_VM_COMMIT,
"CMD_VM_SHUTDOWN":CMD_VM_SHUTDOWN,
"CMD_VM_LIVE":CMD_VM_LIVE
}

COMMIT_PHASE = 1
RUN_PHASE = 2
DEBUG_PHASE = 3