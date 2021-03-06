from datetime import datetime

from trade_terminal import db, TradeProfile
from trade_terminal.exmo import ExmoAPI


class ExmoCurrency(db.Model):
    """docstring for Currency"""
    id = db.Column(db.Integer, primary_key=True)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchange.id'))
    ticker = db.Column(db.String(24))

    def __repr__(self):
        return '<Currency {}>'.format(self.ticker)


class ExmoPair(db.Model):
    """docstring for PairSettings"""
    id = db.Column(db.Integer, primary_key=True)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchange.id'))
    ticker = db.Column(db.String(24))
    orders = db.relationship('ExmoOrder', backref='pair', lazy=True)

    # * Exchange pair_settings:
    min_quantity = db.Column(db.Float)  # minimum quantity per order
    max_quantity = db.Column(db.Float)  # maximum quantity per order
    min_price = db.Column(db.Float)  # minimum order price
    max_price = db.Column(db.Float)  # maximum order price
    min_amount = db.Column(db.Float)  # minimum order amount
    max_amount = db.Column(db.Float)  # maximum order amount

    def __init__(self, exchange_id, ticker):
        self.exchange_id = exchange_id
        self.ticker = ticker
        self.update_pair_settings()

    def update_pair_settings(self):
        get_settings = ExmoAPI().pair_settings()
        self.min_quantity = get_settings[self.ticker]['min_quantity']
        self.max_quantity = get_settings[self.ticker]['max_quantity']
        self.min_price = get_settings[self.ticker]['min_price']
        self.max_price = get_settings[self.ticker]['max_price']
        self.min_amount = get_settings[self.ticker]['min_amount']
        self.max_amount = get_settings[self.ticker]['max_amount']

    def __repr__(self):
        return '<Pair {}>'.format(self.ticker)


class ExmoOrder(db.Model):
    """docstring for UserOrder"""
    id = db.Column(db.Integer, primary_key=True)
    trade_profile_id = db.Column(db.Integer, db.ForeignKey('trade_profile.id'))
    pair_id = db.Column(db.Integer, db.ForeignKey('exmo_pair.id'))
    status = db.Column(db.String(24))  # stop-loss||take-profit||open||cancel

    # * Exchange order settings:
    # order_id = db.Column(db.BigInteger)  # order id
    order_id = db.Column(db.String(24))
    created = db.Column(db.DateTime)  # date and time of order creation
    order_type = db.Column(db.String(24))  # (market)_buy||sell_(total)
    price = db.Column(db.Float)  # order price
    quantity = db.Column(db.Float)  # quantity per order
    amount = db.Column(db.Float)  # order amount

    # ! Relationship

    trades = db.relationship('ExmoOrderTrades', backref='order', lazy=True)

    def __init__(self, trade_profile_id, ticker, status, order_id):
        self.trade_profile_id = trade_profile_id
        self.pair_id = ExmoPair.query.filter_by(ticker=ticker).first().id
        self.status = status
        self.order_id = order_id
        self.get_order_params(order_id)

    def get_order_params(self, order_id):
        trade_profile = TradeProfile.query.get(self.trade_profile_id)
        current_pair = ExmoPair.query.get(self.pair_id)
        user_open_orders = ExmoAPI(
            trade_profile.public_key,
            trade_profile.secret_key).user_open_orders()
        current_order = user_open_orders[current_pair.ticker]
        for item in current_order:
            if item['order_id'] == str(order_id):
                self.order_id = item['order_id']
                self.created = datetime.fromtimestamp(int(item['created']))
                self.order_type = item['type']
                self.price = item['price']
                self.quantity = item['quantity']
                self.amount = item['amount']

    def __repr__(self):
        return '<ExmoOrder_id {}>'.format(self.order_id)


class ExmoOrderTrades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exmo_order_id = db.Column(db.Integer, db.ForeignKey('exmo_order.id'))

    # * Exchange order settings:
    trade_id = db.Column(db.String(24))  # transaction id
    date = db.Column(db.DateTime)  # transaction date and time
    quantity = db.Column(db.Float)  # quantity per transaction
    price = db.Column(db.Float)  # transaction price
    amount = db.Column(db.Float)  # transaction amount


# class Deal(db.Model):
#     """docstring for Statistic"""
#     id = db.Column(db.Integer, primary_key=True)
#     trade_profile_id = db.Column(db.Integer, db.ForeignKey('trade_profile'))
#     pair = db.Column(db.String(24))
#     direction = db.Column(db.String(24))
#     session = db.Column(db.String(24))
#     open_deal = db.Column(db.DateTime)
#     close_deal = db.Column(db.DateTime)
#     risk_profit = db.Column(db.String(24))
#     setup = db.Column(db.String(24))
#     result = db.Column(db.String(24))
#     status = db.Column(db.String(24))
