import cmq_book
import cmq_market_data
import datetime
import cmq_risk_engine

def test():
    book = cmq_book.get_book_from_db('BOF', status=[2])
    mkt_data = cmq_market_data.load_market_data(book.mkt_deps, value_date = datetime.date(2017,9,29))
    req_greeks = ['pv','cmdelta','cmgamma','cmvega']
    re = cmq_risk_engine.CMQRiskEngine(book, mkt_data, req_greeks)
    re.run_risk()


