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
                       "cookie": '_ga=GA1.1.313319009.1716437715; nsit=pb3S1KorC_kVDvL-een9uzho; AKA_A2=A; _abck=1A23B1D24482B0B0DBACF4CF84C7525F~0~YAAQWgw0F18cf6SPAQAAG4gApQs7FQe1d53Q4ndR6AgOKsF0SWWEEKsdCTLdu2QThQpeRXdrS1RbSTkWgJy7RkgaS4067ey60pu8oCA3oDdvOd+xh063lnepvGzCludK8VFUArNrZl9I7atrC1oqKlfBiD3aqg1M8n6Ko5UVS7BR4X0UmlujlG26rbnKHwtUA/SPodvhq+ALn0fn6n8B/qluvqa15fn7EhraHCmIdlowQfiq+Pfk5RBTkBMekrkWyeDLFIU7E6Xz7sgbeJZTFK4KrSXj/CH5M385buNthzIRFIxINobGu5JUCPT3G8igNXbarFraeoeeSlu3ps7xWiZDHW8b+W1EvqCjY8LA5tciYQk/KBQR6cvPNCELUQdCrwplqeZ0N8fz6j9ggHUndBTKz+S63X8wksE=~-1~-1~-1; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTcxNjQ2MjI3NSwiZXhwIjoxNzE2NDY5NDc1fQ.SUQ1hBhY87AFva8nL1PNa_0gzjXfn_dPqg7QtELX6QA; bm_mi=D86BCB21BE5A0013F226E11D0E941407~YAAQWgw0FwTVgKSPAQAAiM4fpRd46CgFq5dsDN/pcV8ynDYMdIZmxwTCOXruIgRBBp1gsqwU3KfQ1Xb6d7aIjErjgwkjUf/Y20RIp7SO48VP9ijy4vKo0EuadAG9dHkjWKLRktvDB7ITMhNHR6YcDfmSPbGj1ebH8mJc5z3vJQAVCFsO6jIL6CcSHANN9bWACZtjUP1U9tDq+NUt7/7HkZue4qvW6NlVcSxsgrZmzQkFvlcLALjETTcnk9X1IWTO5+evyfl29kWFgzfdy93J/bDZ1eEmrLmUJ+cxvtKTPCMioJ/tB/mrlt0AgHBzL0h2DFDgK1b99Nyp3H8=~1; bm_sz=6621779D19AFBE022EEBD337F8C4701A~YAAQWgw0FwbVgKSPAQAAiM4fpRfVSZxFp0iU5Ih1s0dfXaxQ3ZzakWdViuUKnFBeGu5yBJMwaStSoCJmID1d9etFtymgSw2pAV85EFeNMEYDqKy6rFCD9NM3u5tnlMWZ/EqqyjbHrLUzhLTOqZYECWYxv5HeyO7akPxOITkwwIj5ubO8935QELKgmjHEJ8Fv4yVSHa1WIeZkj2LVft1m6DrJH1m/EySVR/5P+0Pm+ymypEELFYiKrI6Q83p5DX8OAJUgALaDBUDXDh1ZV9XnDCM5jQXF7pWbu1CvhixsVTVjSxufId+i5OCXFz7sorcyXUpPWnzpSMFsQIasmmYXLhlay0N9vgbhCO5jo3HnmcCQESkuEaFMdEmSRGCPMUxxdYLemUhBp23UHueVFlCq4ve60AaqznrB~3553584~4277298; defaultLang=en; ak_bmsc=581E54003B19B9759C846DA09F15CCF5~000000000000000000000000000000~YAAQWgw0FwTWgKSPAQAAwd4fpRf8S/gmJxaTOjwGtWan2qUc8YA7W7WRpCiTymod7nmkDZmb2PEbAiRHD2hR0Q78dA8a8KjijpDqTh0nz7IS91iKxBWFW6XONhATU+z9K1+MR1O6v7XTxTemFLGOmEgtfByHzPlN5IIOcn7MOTt0lJAjvPx7rIwwhHww7OL1y3SEF1wdqWvAgUeWzJmJ1xlAGRjOwSF67nlN9eJp2Un68yPsQYZWm/5HVX4RM4JJWzmBqddXlUuMpW6gbdw0XjbwK49DINT3hrfkW8sPNbw2mlK1/ufKD9kDSFcveFW0aUtgTfxJVplwu2fc41KiSff40NDLmMEOl8WwOIgon/UfEISv3hrpQA3TacDd3qwGiZrzVAAHzUuFy4ac8s7/uhUpLYoRP+/Hgm+VyVK/cNUgVg9la1Dpc8TW4OyJR71Cgfy9i7TZBy5jCaWP7KARwHJZDsdhs03kXmRXMmeIcNfmMSzdWZfzsBTaeMvvo6N62mE=; RT="z=1&dm=nseindia.com&si=46ab8fb0-60c3-444a-9d3b-73b95d5d7f1f&ss=lwj5bj61&sl=1&se=8c&tt=46d&bcn=%2F%2F17de4c12.akstat.io%2F&ld=4y6&nu=kpaxjfo&cl=91t"; _ga_QJZ4447QD3=GS1.1.1716462285.4.0.1716462286.0.0.0; _ga_87M7PJ3R97=GS1.1.1716462279.5.1.1716462286.0.0.0; bm_sv=339ADC157AA98E5233A1CC6CDB66D23B~YAAQWgw0F1HXgKSPAQAAKvcfpRfj2YXrW4gpfHTekPl1tIChHQYIDx4trF+aurgocwgLLl+5VKSdBvlK86JvbTXJHmrTjtLwBvfLxOPVhYG+NR9zCpeGSgVjcIv0c+M4dNGuxnBNpgpC9z4FxchudyVuTMU0qe1DkeI2CMGzRhrGd8XHJw6hXQskNPj8H/h05zQTIpf0cizprt0NE0k9tPNhvwjxvMu0fAdHAUit7C++ej5fKr7l9l+JtOllKCNnihw=~1'
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
    st.write(f'{ticker} LTP:', stock_ltp)

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

