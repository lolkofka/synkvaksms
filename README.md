# VAKSMS API for Python 3

<div align="center">

[![lolkof - SYNKVAKSMS](https://img.shields.io/static/v1?label=lolkof&message=SYNKVAKSMS&color=blue&logo=github)](https://github.com/lolkofka/synkvaksms "Go to GitHub repo")

[VAKSMS Official documentation](https://vak-sms.com/api/vak/)

</div>

## About

This library is a wrapper for the https://vak-sms.com/api/vak/ API **from enthusiasts**. All methods are described and all types are
**explicitly** defined. Methods that create requests to
https://vak-sms.com/api/vak/
return a pydantic's models for each response. Please write about all problems related to the library
to [issues](https://github.com/lolkofka/synkvaksms)

API is up-to-date as of *22 May 2025*.

* PyPl - https://pypi.org/project/synkvaksms/
* Github - https://github.com/lolkofka/synkvaksms
* Requirements: Python >= 3.10

### Features

* You can use **multiple** clients to work with **multiple** users or shops
* **All methods** for working with API are implemented
* The library returns strictly typed for responses from APIs
* For each method, **docstrings** are used
* The library handle {type: error} responses and throws VaksmsBadRequest exception
* **Modern**, strict code for Python 3.10+

## Library Installation

* Install via pip: `pip install synkvaksms`
* Download sources - `git clone https://github.com/lolkofka/synkvaksms`

## Getting Started

### first steps (best practic)

```python
from synkvaksms import Vaksms


def main():
    client = Vaksms('TOKEN') # use vaksms.com domain (not work in russia)
    client = Vaksms('TOKEN', base_url='https://moresms.net') # work in russia

    number = client.get_number('ya')
    print(number.tel)  # 79995554433

    # recieve smscode
    sms_code = number.wait_sms_code(timeout=300, per_attempt=5) # do not indicate timeout and per_attempt
    print(sms_code) #1234

    # set status
    number.set_status('end')
    # bad - ban number
    # end - cancel number
    # send - new sms


main()
```

### Get user balance

```python


from synkvaksms import Vaksms


def main():
    client = Vaksms('TOKEN') # use vaksms.com domain (not work in russia)
    client = Vaksms('TOKEN', base_url='https://moresms.net') # work in russia
    balances = client.get_balance()
    print(balances)  # balance = 100.0


main()
```

### Get number count

```python


from synkvaksms import Vaksms

def main():
    client = Vaksms('TOKEN') # use vaksms.com domain (not work in russia)
    client = Vaksms('TOKEN', base_url='https://moresms.net') # work in russia
    
    data = client.get_count_number('cp')
    print(data)  # service='cp' count=4663 price=18.0


main()
```

### Get country list

```python


from synkvaksms import Vaksms


def main():
    client = Vaksms('TOKEN') # use vaksms.com domain (not work in russia)
    client = Vaksms('TOKEN', base_url='https://moresms.net') # work in russia
    data = client.get_country_list()
    print(data)  # [CountryOperator(countryName='Tajikistan', countryCode='tj', operatorList=['babilon mobile', 'beeline', 'megafon', 'tcell']), CountryOperator(countryName='Zimbabwe', countryCode='zw', operatorList=['econet', 'netone', 'telecel'])... ]


main()
```

### Get number

```python


from synkvaksms import Vaksms


def main():
    client = Vaksms('TOKEN') # use vaksms.com domain (not work in russia)
    client = Vaksms('TOKEN', base_url='https://moresms.net') # work in russia
    data = client.get_number('ya')
    
    # An exclusive function for obtaining the lifetime of a number
    # all known services whose lifetime differs from the standard 20 minutes
    # are included in the library database as of 10/02/2024
    # also work with "rent=True" parameter
    print(data.lifetime) # 1200 lifetime from date of purchase
    print(data.lives_up_to) # 1727823949 unix time of death
    
    print(data)  # tel=79296068469 service='ya' idNum='1725546315697382' lifetime=1200 lives_up_to=1727823949


main()
```

### Recieve smscode

```python


from synkvaksms import Vaksms


def main():
    client = Vaksms('TOKEN')  # use vaksms.com domain (not work in russia)
    client = Vaksms('TOKEN', base_url='https://moresms.net')  # work in russia
    data = client.get_sms_code('1725546315697382') # 1725546315697382 is number id (idNum)
    print(data)  # smsCode='1234'


main()
```

### request a new sms

```python


from synkvaksms import Vaksms


def main():
    client = Vaksms('TOKEN') # use vaksms.com domain (not work in russia)
    client = Vaksms('TOKEN', base_url='https://moresms.net') # work in russia
    data = client.set_status('1725546315697382', 'send') # 1725546315697382 is number id (idNum)
    print(data)  # ready


main()
```

### get service full name, service info, service icons
### this method not in official vaksms documentation

```python


from synkvaksms import Vaksms


def main():
    client = Vaksms('TOKEN') # use vaksms.com domain (not work in russia)
    client = Vaksms('TOKEN', base_url='https://moresms.net') # work in russia
    data = client.get_count_number_list()
    print(data)  # {'mr': Service(name='VK - MailRu', icon='https://vak-sms.com/static/service/mr.png', info='Тут можно принять смс от сервисов VKGroup.Не забывайте проверять номера на занятость через восстановление. Подробнее в базе знаний - https://bit.ly/3M6tXup', cost=22.0, rent=False, quantity=41153, private=False), ... }
    print(data['mr'].name) # VK - MailRu
    

main()
```

## Contact

* E-Mail - lolkofprog@gmail.com
* Telegram - [@lolkof](https://t.me/lolkof)

## License

Released under [GPL](/LICENSE) by [@lolkofka](https://github.com/AioSmsProviders).