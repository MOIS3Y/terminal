import os
import click
from flask.cli import with_appcontext

from trade_terminal import db
from trade_terminal import User, TradeProfile, Exchange
from trade_terminal.exmo import Pair


@click.command(name='create_database')
@with_appcontext
def create_database():
    db.create_all()


@click.command(name='create_users')
@with_appcontext
def create_users():
    one = User(username='One')
    one.set_password('one')
    print('Created: ', one.__repr__())
    two = User(username='Two')
    two.set_password('two')
    print('Created: ', two.__repr__())
    three = User(username='Three')
    three.set_password('three')
    print('Created: ', three.__repr__())

    db.session.add_all([one, two, three])
    db.session.commit()


@click.command(name='create_exchange')
@with_appcontext
def create_exchange():
    exmo = Exchange(name='Exmo')
    print('Created: ', exmo.__repr__())

    db.session.add(exmo)
    db.session.commit()


@click.command(name='create_trade_profile')
@with_appcontext
def create_trade_profiles():
    secret_key = os.environ.get('EXCHANGE_SK') or 'S-pass'
    public_key = os.environ.get('EXCHANGE_PK') or 'K-pass'
    first = TradeProfile(
        user_id=1,
        exchange_id=1,
        name='TestAcc',
        secret_key=secret_key,
        public_key=public_key)
    print('Created: ', first.__repr__())

    db.session.add(first)
    db.session.commit()


@click.command(name='create_pair')
@with_appcontext
def create_pair():
    eth_rub = Pair(exchange_id=1, ticker='ETH_RUB')
    print('Created: ', eth_rub.__repr__())
    btc_rub = Pair(exchange_id=1, ticker='BTC_RUB')
    print('Created: ', btc_rub.__repr__())

    db.session.add_all([eth_rub, btc_rub])
    db.session.commit()


if __name__ == "__main__":
    print(os.environ.get('EXCHANGE_SK'))