# DomainTracker

## Installation
Just install the dependencies with the following command:

`pip install -r requirements.txt`

## Usage

Track the availability of domains. Usage:

```
python domaintracker.py (hello)x(world,you)x(.com,.net)
```

This call will check the following domains:
- `helloworld.com`
- `helloyou.com`
- `helloworld.net`
- `helloyou.net`

By default, the domains are shown at the standard output. You can also use other output methods. For example, the following code will create a CSV file with the results:

```
python domaintracker.py (hello)x(world,you)x(.com,.net) -o domains.csv
```