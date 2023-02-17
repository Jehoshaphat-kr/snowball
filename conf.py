import snowball as sb
# import pandas as pd

# print(sb.ecosSymbol)
# col_table = pd.concat(
#     objs={
#         "수신신규 121Y002":sb.ecosContains('121Y002').이름.drop_duplicates(keep='first'),
#         "수신잔액 121Y013":sb.ecosContains('121Y013').이름.drop_duplicates(keep='first'),
#         "대출신규 121Y006":sb.ecosContains('121Y006').이름.drop_duplicates(keep='first'),
#         "대출잔액 121Y015":sb.ecosContains('121Y015').이름.drop_duplicates(keep='first'),
#     }, axis=1
# )
# print(col_table)
# print(sb.ecosLoad('722Y001', '한국은행 기준금리'))
# print(sb.ECOS.TY1Y)
# print(sb.ECOS.USDExchange)
# print(sb.KRSE.wics)
# print(sb.KRSE.wi26)
# print(sb.indexList)

# kospi = sb.TimeSeries('1001')
# print(kospi.ohlcv)

# samsung = sb.TimeSeries('005930')
# print(samsung.ohlcv)

# ind = sb.TimeSeries('817Y002', '회사채(3년, AA-)')
# print(ind.ohlcv)

# tsla = sb.TimeSeries('AAPL')
# print(tsla.ohlcv)

ty10y = sb.TimeSeries('DGS10')
print(ty10y.ohlcv)