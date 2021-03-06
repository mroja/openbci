"""
Predefined message types.
"""

INVALID_REQUEST = 'INVALID_REQUEST'
INTERNAL_ERROR = 'INTERNAL_ERROR'
HEARTBEAT = 'HEARTBEAT'

PEERS_READY = 'PEERS_READY'
PEERS_READY_RECEIVED = 'PEERS_READY_RECEIVED'

OK = 'OK'
ERROR = 'ERROR'

QUERY = 'QUERY'
REDIRECT = 'REDIRECT'

BROKER_HELLO = 'BROKER_HELLO'
BROKER_HELLO_RESPONSE = 'BROKER_HELLO_RESPONSE'

BROKER_REGISTER_PEER = 'BROKER_REGISTER_PEER'
BROKER_REGISTER_PEER_RESPONSE = 'BROKER_REGISTER_PEER_RESPONSE'

BROKER_HEARTBEAT = 'BROKER_HEARTBEAT'
BROKER_HEARTBEAT_RESPONSE = 'BROKER_HEARTBEAT_RESPONSE'

BROKER_REGISTER_QUERY_HANDLER = 'BROKER_REGISTER_QUERY_HANDLER'
BROKER_UNREGISTER_QUERY_HANDLER = 'BROKER_UNREGISTER_QUERY_HANDLER'
