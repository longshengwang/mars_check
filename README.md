# Mars Check Command Tools

## local command install
1. `pip install .`
2. add `eval "$(register-python-argcomplete mcheck)"` to `.bashrc`
3. use `mcheck` command at terminal
> the second step can support tab help

```
~ mcheck --help
--help   -h       check    compare  config   log      show     snap
```

## update for local command 
```
$ pip uninstall mcheck
$ pip install .
```

## 1. config
- mars url (https://127.0.0.1)
- user
- password  
```
usage: main.py config [-h] [-u USER] [-p PASSWORD] [--url URL]

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  The mars user name.
  -p PASSWORD, --password PASSWORD
                        The mars password.
  --url URL             The mars host url.(Example: https://192.168.1.20)
```  

## 2. snap
- get the data( device/device_config/links/hosts/flows/groups ) from mars, and save to local file system
- list all snap time
- list all the snap summary
- delete the selected time
```
usage: main.py snap [-h] (-l | -d | -g | -s)

optional arguments:
  -h, --help     show this help message and exit
  -l, --list     List all the snap data.
  -d, --delete   Delete the select data.
  -g, --get      Snap all the data.
  -s, --summary  Show the summary of all times.
```

## 3. check
- check online data
- check the last snap data
- check the selected snap data
```
usage: main.py check [-h] (-o | -s | -l)

optional arguments:
  -h, --help       show this help message and exit
  -o, --online     Check the online data.
  -s, --snap_time  Check the data from snap data.
  -l, --last_snap  Check the last snap data.
```

## 4. compare
- flow (can specify device)
- group (can specify device)
- host
- link
```
usage: main.py compare [-h] [-d DEVICE] (-l | -f | -g | -ho)

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        Specify device for flow or group.
  -l, --link            Only compare link data.
  -f, --flow            Only compare flow data.
  -g, --group           Only compare group data.
  -ho, --host           Only compare host data.
```

# 5. log 
>Get the log data from elasticsearch.
- specify the key word for search 
- set the count items of search data
- set the start search time
```
usage: main.py log [-h] [-w WORD] [-l LAST_HOURS] [-c COUNT]

optional arguments:
  -h, --help            show this help message and exit
  -w WORD, --word WORD  The filter keyword.
  -l LAST_HOURS, --last_hours LAST_HOURS
                        The last hours.(Default is 2)
  -c COUNT, --count COUNT
                        The log count.(Default is 1000)
```

# 6. show
> can specify online/last_snap/selected_snap
- show devices
- show hosts
- show links  
```
usage: main.py show [-h] [-o | -s | -l] {device,link,host} ...

positional arguments:
  {device,link,host}
    device            Show devices.
    link              Show links.
    host              Show hosts.

optional arguments:
  -h, --help          show this help message and exit
  -o, --online        Show the online data.
  -s, --snap_time     Show the selected snap data.
  -l, --last_snap     Show the last snap data.
```