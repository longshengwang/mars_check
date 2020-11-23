from os.path import expanduser

ETH_TYPE_CODE = {
    '0x800': 'IPv4',
    '0x806': 'ARP',
    '0x86dd': 'IPv6',
    '0x8847': 'MPLS',
    '0x8848': 'MPLS',
    '0x8863': 'PPPoE',
    '0x8864': 'PPPoE',
    '0x88cc': 'LLDP',
    '0x8942': 'BDDP',
}


DEVICE_CONFIG_NAME = 'devices_config'
DEVICE_NAME = 'devices'
FLOW_NAME = 'flows'
GROUPS_NAME = 'groups'
HOSTS_NAME = 'hosts'
LINKS_NAME = 'links'


DEFAULT_CONFIG_PATH = expanduser("~") + '/.mars_check/'
MAX_BACKUP_COUNT = 20

URL_CONFIG_FILE = '.url'
USER_CONFIG_FILE = '.user'
PASSWORD_CONFIG_FILE = '.password'
