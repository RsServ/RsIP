# RsiP

Simple Tor exit IP rotation tool for Linux.

> RsiP changes the public exit IP seen through Tor. It does not change your ISP-assigned IP.

## Install

```bash
git clone <YOUR-GITHUB-URL>
cd RsiP
sudo ./install.sh
```

## Usage

```bash
rsip status
rsip rotate
rsip start --interval 10
rsip stop
```

### Commands

* `rsip status` — Show current Tor exit IP
* `rsip rotate` — Request a new Tor identity
* `rsip start --interval 10` — Rotate every 10 seconds
* `rsip stop` — Stop rotation

## Requirements

* Kali Linux / Debian
* Tor
* Python 3
* Internet connection

The installer configures Tor ControlPort on `127.0.0.1:9051`.

## Credits

```text
RsServ
RsiP v1.0
```
