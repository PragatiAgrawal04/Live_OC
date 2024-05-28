import requests
import pandas as pd
import numpy as np
import time
import xlwings as xw
from bs4 import BeautifulSoup
import datetime
import streamlit as st
import csv

st.set_page_config(page_title="Dashboard", layout="wide")

TWO_PERCENT_MARKET_PRICE = 0.0

exchange = "NSE"


def last_thursdays(year):
    exp = []
    for month in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
        if month == 1 or month == 2 or month == 3 or month == 4 or month == 5 or month == 6 or month == 7 or month == 8 or month == 9:
            date = f"{year}-0{month}-01"
        if month == 10 or month == 11 or month == 12:
            date = f"{year}-{month}-01"

        # we have a datetime series in our dataframe...
        df_Month = pd.to_datetime(date)

        # we can easily get the month's end date:
        df_mEnd = df_Month + pd.tseries.offsets.MonthEnd(1)

        # Thursday is weekday 3, so the offset for given weekday is
        offset = (df_mEnd.weekday() - 3) % 7

        # now to get the date of the last Thursday of the month, subtract it from
        # month end date:
        df_Expiry = df_mEnd - pd.to_timedelta(offset, unit='D')
        exp.append(df_Expiry.date())

    return exp


today_year = datetime.datetime.now().year
exp_date_list = last_thursdays(today_year)
DATE_LIST = []
TODAY = datetime.date.today()
for i in range(len(exp_date_list)):
    x = (exp_date_list[i] - TODAY).days
    if x > 0:
        DATE_LIST.append(exp_date_list[i].strftime('%d-%m-%Y'))
EXP_OPTION = DATE_LIST[0]


def current_market_price(ticker, exchange):
    url = f"https://www.google.com/finance/quote/{ticker}:{exchange}"

    for _ in range(1000000):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        class1 = "YMlKec fxKbKc"

        price = float(soup.find(class_=class1).text.strip()[1:].replace(",", ""))
        yield price

        time.sleep(5)


def get_dataframe(ticker, exp_date_selected):
    while True:
        try:

            url = f"https://www.nseindia.com/api/option-chain-equities?symbol={ticker}"
            headers = {"accept-encoding": "gzip, deflate, br, zstd",
                       "accept-language": "en-US,en;q=0.9",
                       "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                       "cookie": '_ga=GA1.1.1832904179.1695643771; _ga_PJSKY6CFJH=GS1.1.1698408521.20.1.1698410308.60.0.0; defaultLang=en; nsit=8D8ghplcs_OYdm_OlPOtWqbx; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTcxNjg4NTI4MCwiZXhwIjoxNzE2ODkyNDgwfQ.oSI2zT4hBeXNLp_LPgcuJHJiaetbn1aKOrhCiCnWPCc; AKA_A2=A; bm_mi=5B8E0C6640C8D32AF92C4067A45EE8E0~YAAQPvTfF5YxxLiPAQAArllWvhexc6c/t0aOzliXQ+aCT71zzabIttnX3sCDvWwRjaava4pVKI/CPKnl7CvkCHWdkbgtZuXfKgSr8OI9e4IrdVK8ZY6yESVm48EeGTWkyQIq+FCQQQXcNw3qsk1tY80E3q7aaU4RqZ0UN4JG1P1LG0E5FXpZB4JEkIA3pVDlQZebFZzyw3mRY3FOkjjdfEZE15//x/PWhmd+eg5bcpvQ3wNElTkBcsWxExgCvjkvR94O8yg0V7BkDlBa7vDFtUv+wWL1jO//2HIr9iRjsJKzMpP0p9OWojzGzPIIdKvWUrp9qYQS5vN5Xj4=~1; bm_sz=C4EE855B350EC0B4DAE73E4EAB3FE567~YAAQPvTfF5gxxLiPAQAArllWvhd+apTQbSycVaXKqp2a8iWx9v+DgmPbVi79i2aipkfEWTWE+0C0Td/z4IKG+eUKHEW+hJbiD14ejbvlAeBlppF9TkVFONNNxLK94RevSpy6A56xc0GHeFoyTTIHMXMf7zuUzp9dmNaYxH+9PLVxWVevFNPnkWLNMOUOtKMIZohwLNJNCeo8LOgGCNib3yOyrbPIZ7kgmp8m2sK5VpvGFlnT3pTUty074dlqlcrOztdKacdCX+BTrz18QTTLIAmHYD7w6Eug+kbNQNQcMbkFFcztSsxpTCMuV/SvtnD4OWGlvHZ3eSwILQHtY/vojD0iHmmLRIkQtL9ldWfOQiywB8q09xfgXIu7qDjELyTSX6bwSPlepZ59zuwsFkSQcESHx7D791UT3+q9AuB8wgzSCpcOTvZMrlOg3/1pvQuWnFfhr252UbFs~3752756~4276788; ak_bmsc=280E6F19359FC052E7741F493F72495E~000000000000000000000000000000~YAAQPvTfF1wyxLiPAQAAnGFWvheOdl+YNetwwNYDnf9+QljQ/8Hf402W4n7S/o6y9IY/NvZDM1Sg4hfp8IFMpsVT6PfJOCWjQWXoo3i/OOM4HyBID6a45qywAkE3IYMknMwz56kRPq8Qg8LRPCP0IEMkM5icXQDA5rw/koKT5POer5tRfZRBrlHPJnbn1gRWofJlaok7hfjnCLBSkoIGTUA1pcbGjsdVQH8qCTB9TngHVyugdn6Xk2d+g9WfjuTwqxTLvYlMa87ckRxmmLBLPJgtNQTUSGq98J764TrH2eYBqRZ6KlGDXOLrkNAWJK8Ejpp6epY27Ut1yvzUGbsy8dQBfVfjKEveVbPuA84dy/rl3sbpbHXmsbewcjoSngb0+FWXeE7DGRlmKaTaU0qqSB/7QiYUhP0fZ24tGtEotXzIxCTULjxsQ2H9wv9CyHVITupF906IDeASnveRTL0HJKnzUNLhCy8fkA6H9563HXNWtlW1vm6Y9T7SYQA=; _ga_QJZ4447QD3=GS1.1.1716885277.17.0.1716885292.0.0.0; _ga_87M7PJ3R97=GS1.1.1716885277.22.1.1716885292.0.0.0; _abck=EE00CD6FB797BDCFA4B799A810836AA8~0~YAAQPvTfFzg0xLiPAQAA14VWvgv2XgwyfAnd3uv/W7inzTTXaZruGieNyJ2y7TTcF6p2BfL6hAPz4Xk0EnTZXqXgNcT25CePI9wkv3EcSLXYVr5SGGU98YDXzQReeKttSU/7E7iD418l5h9+4TFlpoaQ1/r5UWs3Mb0RI0PziPwoNchmmv+ySSG/QQ3f76gGgOLxRTkCOa1310nkG7WbPZpleO7YjR/7zheqpeukR3QHd8iYe10vfQLyW1AhS3mcNueBvA76yDZSBSoTQ1cZnncuaReKgFgl4PpY5P8CSc4ZvrFlG0tcbuHelkOzkLxgNOn8IIrzRkmWZF0jdYKhGiheIQXAyB2um7ywywEUnxK4J2eU6wD+sgPBvjW5wYIf~-1~-1~-1; bm_sv=07CBB4EB808666BD57D562937A5A5D92~YAAQPvTfFzk0xLiPAQAA14VWvhdIR3l7E980ex5juDJiI+m/LnYrXiDqd64JmYQ0PtRxAeNDEzCn5f0p7rIFN4Rjv6lC5EMdoKC+62LVzWxhMAs0+6lEBorpwzUIZNm+3A/22lQN81kxrHtPfzjRBGi9zrY2zGrYCwDBzImWIaH+2aozFGI3An1+h04Kaj+s1Tq7ON3qb6fi9M1QdMEfSK33J9Mc0bQAc6EO3L2kL7oibhwg8mbAqJa7IeSVzeB64wAa~1'
                      }
            session = requests.Session()
            data = session.get(url, headers=headers).json()["records"]["data"]
            ocdata = []
            for i in data:
                for j, k in i.items():
                    if j == "CE" or j == "PE":
                        info = k
                        info["instrumentType"] = j
                        ocdata.append(info)

            df = pd.DataFrame(ocdata)
            # wb = xw.Book("optionchaintracker.xlsx")
            # st = wb.sheets("vedl")
            # st.range("A1").value = df
            # print(df)

            # expiry_dates = df['expiryDate'].unique().tolist()
            # fin_exp_dates = []
            # for i in expiry_dates:
            #     temp_expiry = datetime.datetime.strptime(i, '%d-%b-%Y')
            #     fin_exp_dates.append(temp_expiry.strftime('%d-%m-%Y'))

            strikes = df.strikePrice.unique().tolist()
            strike_size = int(strikes[int(len(strikes) / 2) + 1]) - int(strikes[int(len(strikes) / 2)])

            for price in current_market_price(ticker, exchange):
                two_percent_cmp = price + 0.02 * price
                TWO_PERCENT_MARKET_PRICE = two_percent_cmp
                break

            print(TWO_PERCENT_MARKET_PRICE)

            # access dataframe for atm price
            atm = int(round(TWO_PERCENT_MARKET_PRICE / strike_size, 0) * strike_size)
            print(atm)

            output_ce = pd.DataFrame()

            atm_pe = atm
            output_pe = pd.DataFrame()

            for _ in range(5):

                # (for ce)
                ab = True
                while ab:

                    fd = df[df['strikePrice'] == atm]

                    if fd.empty:
                        print("empty df ce", atm)
                        atm = atm + 0.5
                        if atm > strikes[-1]:
                            break
                    else:
                        ab = False

                # print(fd)

                # (for pe)
                ab_pe = True
                while ab_pe:

                    fd_pe = df[df['strikePrice'] == atm_pe]

                    if fd_pe.empty:
                        print("empty df pe", atm_pe)
                        atm_pe = atm_pe - 0.5
                    else:
                        ab_pe = False

                # print(fd_pe)

                # (for ce)convert expiry date in particular format
                fd = fd.reset_index()
                for i in range(len(fd)):
                    expiry_date_str = fd["expiryDate"].iloc[i]
                    temp_expiry = datetime.datetime.strptime(expiry_date_str, '%d-%b-%Y')
                    result_expiry = temp_expiry.strftime('%d-%m-%Y')
                    fd.at[i, "expiryDate"] = result_expiry
                # print(fd)
                # print(type(fd["expiryDate"].iloc[0]))

                # (for pe) convert expiry date in particular format
                fd_pe = fd_pe.reset_index()
                for i in range(len(fd_pe)):
                    expiry_date_str_pe = fd_pe["expiryDate"].iloc[i]
                    temp_expiry_pe = datetime.datetime.strptime(expiry_date_str_pe, '%d-%b-%Y')
                    result_expiry_pe = temp_expiry_pe.strftime('%d-%m-%Y')
                    fd_pe.at[i, "expiryDate"] = result_expiry_pe

                adjusted_expiry = exp_date_selected
                adjusted_expiry_pe = exp_date_selected

                # (subset_ce (CE))
                subset_ce = fd[(fd.instrumentType == "CE") & (fd.expiryDate == adjusted_expiry)]
                # print(subset_ce)
                output_ce = pd.concat([output_ce, subset_ce])

                # (subset_pe (PE))
                subset_pe = fd_pe[(fd_pe.instrumentType == "PE") & (fd_pe.expiryDate == adjusted_expiry_pe)]
                # print(subset_pe)
                output_pe = pd.concat([output_pe, subset_pe])

                # (for CE)
                atm += strike_size

                # (for PE)
                atm_pe -= strike_size

            output_ce = output_ce[["strikePrice", "expiryDate", "lastPrice", "instrumentType"]]
            output_pe = output_pe[["strikePrice", "expiryDate", "lastPrice", "instrumentType"]]

            output_ce.reset_index(drop=True, inplace=True)
            output_pe.reset_index(drop=True, inplace=True)

            return output_ce, output_pe

        except Exception as e:
            pass


# output_ce, output_pe = get_dataframe()
# print(output_ce)
# print(output_pe)
def highlight_ratio(s):
    if s["CE Premium %"] > 1:
        if s["PE Premium %"] > 1:
            return ['background-color: paleturquoise'] * len(s)
        else:
            return ['background-color: paleturquoise'] * 2 + ['background-color: white'] * 2
    else:
        if s["PE Premium %"] > 1:
            return ['background-color: white'] * 2 + ['background-color: paleturquoise'] * 2
        else:
            return ['background-color: white'] * len(s)





@st.experimental_fragment
def frag_table(table_number, selected_option='UBL', exp_option=EXP_OPTION):

    shares = pd.read_csv("FNO Stocks - All FO Stocks List, Technical Analysis Scanner.csv")
    share_list = list(shares["Symbol"])
    selected_option = selected_option.strip()
    share_list.remove(selected_option)
    share_list = [selected_option] + share_list

    exp_date_list_sel = DATE_LIST.copy()
    print("LIST: ", exp_date_list_sel)
    exp_option = datetime.datetime.strptime(exp_option, "%d-%m-%Y").date().strftime('%d-%m-%Y')
    print("EXP_OPTION:", exp_option)
    exp_date_list_sel.remove(exp_option)
    exp_date_list_sel = [exp_option] + exp_date_list_sel
    #
    # date_list = []
    # today_date = datetime.date.today()
    # for i in range(len(exp_date_list)):
    #     x = (exp_date_list[i] - today_date).days
    #     if x > 0:
    #         date_list.append(exp_date_list[i].strftime('%d-%m-%Y'))
    c1, c2 = st.columns(2)
    with c1:
        selected_option = st.selectbox("Share List", share_list, key="share_list" + str(table_number))
    with c2:
        exp_option = st.selectbox("Expiry Date", exp_date_list_sel, key="exp_list" + str(table_number))
        if selected_option in share_list:
            ticker = selected_option
            output_ce, output_pe = get_dataframe(ticker, exp_option)
            ########################################## Stock LTP and Matrix #######################################
            stock_ltp = 0.0
            for price in current_market_price(ticker, exchange):
                stock_ltp = price
                break

        # ********************************** MATRIX ******************************************
        l1, l2 = len(output_ce), len(output_pe)
        if l1 < l2:
            fin_len = l1
        else:
            fin_len = l2
        matrix = np.zeros((fin_len, 4))
        df = pd.DataFrame(matrix, columns=["CE Premium %", "CE (Premium + SP)%", "PE Premium %", "PE (Premium + SP)%"])

        for i in range(len(df)):
            df.at[i, "CE Premium %"] = round((output_ce["lastPrice"].iloc[i] / stock_ltp) * 100, 2)
            df.at[i, "CE (Premium + SP)%"] = round(
                (((output_ce["strikePrice"].iloc[i] - stock_ltp) + output_ce["lastPrice"].iloc[i]) / stock_ltp) * 100,
                2)
            df.at[i, "PE Premium %"] = round((output_pe["lastPrice"].iloc[i] / stock_ltp) * 100, 2)
            df.at[i, "PE (Premium + SP)%"] = round(
                (((stock_ltp - output_pe["strikePrice"].iloc[i]) + output_pe["lastPrice"].iloc[i]) / stock_ltp) * 100,
                2)

        # ************************************************************************************
    col1, col2, col3 = st.columns(3)

    with col1:
        output_ce = output_ce.style.set_properties(**{'background-color': 'palegreen','font-size': '20pt'})
        output_ce = output_ce.format({'lastPrice': "{:.2f}".format, 'strikePrice':"{:.1f}".format})
        st.dataframe(output_ce)
    with col2:
        output_pe = output_pe.style.set_properties(**{'background-color': 'antiquewhite'})
        output_pe = output_pe.format({'lastPrice': "{:.2f}".format, 'strikePrice':"{:.1f}".format})
        st.dataframe(output_pe)
    with col3:
        df = df.style.apply(highlight_ratio, axis=1)
        df = df.format(formatter="{:.2f}".format)
        st.table(df)
    st.write(f'{ticker} CMP:', stock_ltp)

    if ('share_list2' in st.session_state) and ('share_list3' in st.session_state):
        curr = pd.DataFrame({'table1': [st.session_state["share_list1"]],
                             'exp1': [st.session_state["exp_list1"]],
                             'table2': [st.session_state["share_list2"]],
                             'exp2': [st.session_state["exp_list2"]],
                             'table3': [st.session_state["share_list3"]],
                             'exp3': [st.session_state["exp_list3"]],
                             'timestamp': [datetime.datetime.now()]
                             })
        if len(hist_df) > 30:
            curr.to_csv('history.csv', mode='w', index=False, header=True)
        else:
            curr.to_csv('history.csv', mode='a', index=False, header=False)

hist = pd.read_csv("history.csv")
hist_df = pd.DataFrame(hist)

print(len(hist_df))

if len(hist_df) > 0:
    last_rec = hist_df.tail(1)
    print(last_rec)
    frag_table(1, last_rec['table1'].item(), last_rec['exp1'].item())
    frag_table(2, last_rec['table2'].item(), last_rec['exp2'].item())
    frag_table(3, last_rec['table3'].item(), last_rec['exp3'].item())
else:
    frag_table(1)
    frag_table(2)
    frag_table(3)

