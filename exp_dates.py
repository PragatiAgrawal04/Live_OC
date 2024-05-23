import requests
import pandas as pd
import numpy as np
import time
import xlwings as xw
from bs4 import BeautifulSoup
import datetime
import streamlit as st
st.set_page_config(page_title="Dashboard", layout="wide")

TWO_PERCENT_MARKET_PRICE = 0.0
exchange = "NSE"



def last_thursdays(year):
    exp = []
    for month in [1,2,3,4,5,6,7,8,9,10,11,12]:
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
        exp.append(df_Expiry)

    return exp

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
                       "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                       "cookie": '_ga=GA1.1.1104812566.1715673932; nsit=DXaQ2SbDGa9HsTXhwkNwpTo4; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTcxNjI4NzU3OSwiZXhwIjoxNzE2Mjk0Nzc5fQ.obJiODllMc8QHV25Ky95nMGFJ3bqgViUGSOVC1Hso5g; AKA_A2=A; _abck=AC0A6E579954CFC1BA4A76B56A1628F3~0~YAAQUGDQFwrjO5iPAQAAtSa2mguEKyWD8Exi2JMM7SIB2Vaynvo6hqa8bNg8MT8RY9CTsrBk784kyuiRTl22JTL34Xv0jQlwLyVLKPHnUrz4lbSwiTimmq1bMGiUQWw+Em11vzEBdw/G9nug37QlwBEaasEWcpHtnj3w9TWYMZ1eSw6dIlHIh448u9XdqXUuTjkawbtS2XqmlpQ1y6Plv4DpNWtMbPn1HuvQwwpKeHYou7NOryJWI6xpGiw26NrZSKpygwaEQhi40NbFzl3roBGs3ATgZI0k8jEnwtmWx2ZQIc/ca1DL2PYk2bL+sN70TYRaSF0cRtjVeCDp4Ll5rQtkpfNT+cAOhHQDT41OVocXWNzxDl1bEqnt/z+kNXekY/vUpLdSKPWJ4BeILPf1UQoKAU9mfcN3Nqs=~-1~-1~-1; bm_sz=D7A90F0BFCCC1F46AA3C2A0F601D2669~YAAQUGDQFw3jO5iPAQAAtSa2mhcWvmOKQLomwTNbF4/120ORyM8FDLEcEE/53z6N7+8iw/iMuZwLDBO7KdSIS4v0aB7/VT0uaLdAtpG/Jdh6J56lEFx7pPCO/E1ULJG3rRC14qLsvTiQG7CUG/fZJc7URZcxOkxKjysqIOZAAh5k1KqTb06VYOnHVsyxPCEC0B8tdxuoijb/Imna3lMwCyW17jA54t3DrRpQqfhdxpoA/ujP9fmnYK/EuOhXLpKBRr3Bm2EWWB265O8I4AE3mt9Tgl+7OsciLS52bthRQRkjgj5af2AKDvGuZuIIPehD3Hh/AD6EDjVdnCEly0Qts0l2ViJXFWj6Oyw8BunDAM7TzduFQ+4YgT4RVKslifzS5/m3INx6ylWCoXdrYa4=~3618101~4600901; defaultLang=en; ak_bmsc=4AF4263F444BE2EAB9A49B7DA87AF4CF~000000000000000000000000000000~YAAQUGDQF9TkO5iPAQAA0j62mhcGAPKGh03G8oc3BVV0Vt8xcN/DZ3BykjWCNLAOgjoCn6UD0t4/pbyJMozX+5oxHrj994irKPxyOStQO3uEEReh/oZv7ivp7tKHJdpBpDHC+UkdtrHWkeFOuq8MqXhT/JHaVCbBAxKvZ7+SYQlXl+o3luTRWQz29s+wT8NB4EYe35RB4Xiju5vYSXd7arNjkW7pYy/NBGATBsD7yNFdBWNpKU+zWBlAgKOXtFqVdxjsxNyCIRnlvPGda5WB5dXbqLyq6UeRubz7c2HfG5m3u2BKkcSxA9Ig0U5JwBeKTm+r+xlismoaRPSeFp5mLjx4CLLH0FpKbQLXAh8rYykggPPozxQ+PGiPSTlxgDTpiQxIgKTU85h9l8ZVsx83ak1REOtZAId/ihfZLakV2J5tRKJzuvRVJZ3PVIGn37+QVS9sZ8C8ZkP68n/8rlQT0A==; RT="z=1&dm=nseindia.com&si=a746dd1a-fbf2-473e-a100-db75208eb944&ss=lwg9b7lx&sl=1&se=8c&tt=6nu&bcn=%2F%2F17de4c17.akstat.io%2F&ld=6sk&nu=kpaxjfo&cl=dco"; _ga_QJZ4447QD3=GS1.1.1716287596.18.0.1716287596.0.0.0; _ga_87M7PJ3R97=GS1.1.1716287587.21.1.1716287596.0.0.0; bm_sv=E7CFBC9E4C9334704757FF25BE39EACB~YAAQUGDQF7HnO5iPAQAA0mS2mhflyyKE+VpDSzZ15+LW5diGR/cPGfwPHJ+h0AWnWuMku/t4gKsocmzofK4aq4oJjTD0uFOje2lvNKiUBh4nqBCHRV4RGkMIGW7FX7y+y3flwvrCSVxRVAVxRjScsQKe2SfyJEaABlWGqgSZh+gsa2BWd+MQOvZrq+RaRA6BFgcKz2soanVzzw0+KKj29Zyl3LiHQtYnzXFpCs0wbShdUvmskVhTqfpG7rry+ONqnEU=~1'
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



            expiry_dates = df['expiryDate'].unique().tolist()
            fin_exp_dates=[]
            for i in expiry_dates:
                temp_expiry = datetime.datetime.strptime(i, '%d-%b-%Y')
                fin_exp_dates.append(temp_expiry.strftime('%d-%m-%Y'))
            print(fin_exp_dates)
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
                # # (for ce)convert expiry date in particular format
                fd = fd.reset_index()
                for i in range(len(fd)):
                    expiry_date_str = fd["expiryDate"].iloc[i]
                    temp_expiry = datetime.datetime.strptime(expiry_date_str, '%d-%b-%Y')
                    result_expiry = temp_expiry.strftime('%d-%m-%Y')
                    fd.at[i, "expiryDate"] = result_expiry
                # # print(fd)
                # # print(type(fd["expiryDate"].iloc[0]))
                #
                # # (for pe) convert expiry date in particular format
                fd_pe = fd_pe.reset_index()
                for i in range(len(fd_pe)):
                    expiry_date_str_pe = fd_pe["expiryDate"].iloc[i]
                    temp_expiry_pe = datetime.datetime.strptime(expiry_date_str_pe, '%d-%b-%Y')
                    result_expiry_pe = temp_expiry_pe.strftime('%d-%m-%Y')
                    fd_pe.at[i, "expiryDate"] = result_expiry_pe


                # (subset_ce (CE))
                adjusted_expiry = exp_date_selected
                adjusted_expiry_pe = exp_date_selected
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

@st.experimental_fragment
def frag_table(table_number):
    shares = pd.read_csv("FNO Stocks - All FO Stocks List, Technical Analysis Scanner.csv")
    share_list = list(shares["Symbol"])

    today_year = datetime.datetime.now().year
    exp_date_list = last_thursdays(today_year)
    date_list = []
    today_date = datetime.date.today()
    for i in range(len(exp_date_list)):
        x = (exp_date_list[i].date() - today_date).days
        if x > 0:
            date_list.append(exp_date_list[i].date().strftime('%d-%m-%Y'))
    print(date_list)
    c1, c2 = st.columns(2)
    with c1:
        selected_option = st.selectbox("Share List", share_list, key="share_list"+str(table_number))
    with c2:
        exp_option = st.selectbox("Expiry Date", date_list, key="exp_list"+str(table_number))
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
        df = pd.DataFrame(matrix, columns=["Premium %", "(Premium + SP)%", "Put Ratio", "Put Effective Ratio"])

        for i in range(len(df)):
            df.at[i, "Premium %"] = round((output_ce["lastPrice"].iloc[i] / stock_ltp) * 100,2)
            df.at[i, "(Premium + SP)%"] = round((((output_ce["strikePrice"].iloc[i] - stock_ltp) + output_ce["lastPrice"].iloc[i]) / stock_ltp) * 100,2)
            df.at[i, "Put Ratio"] = round((output_pe["lastPrice"].iloc[i] / stock_ltp) * 100,2)
            df.at[i, "Put Effective Ratio"] = round((((stock_ltp - output_pe["strikePrice"].iloc[i]) + output_pe["lastPrice"].iloc[i]) / stock_ltp) * 100,2)

        # ************************************************************************************
    col1, col2, col3 = st.columns(3)

    with col1:
        print(output_ce)
        #output_ce = output_ce.style.set_table_styles([{'backgroundColor': 'palegreen'}])
        def coloring(val):
            color = "palegreen" if val else "white"
            return f"background-color: {color}"

        output_ce = output_ce.style.applymap(coloring)
        output_ce.format("{:.2%}")
        st.dataframe(output_ce)
    with col2:
        #output_pe = output_pe.style.set_properties(**{'background-color': 'antiquewhite'})
        st.dataframe(output_pe, column_config = {'strikePrice':'Strike Price',
                                                'expiryDate':'Expiry Date',
                                                'lastPrice':st.column_config.NumberColumn("Last Price",format="%.2f"),
                                                'instrumentType':'Instrument'})
    with col3:
        df = df.style.format(formatter="{:.2f}".format)
        st.table(df)
    st.write(f'{ticker} LTP:', stock_ltp)


frag_table(1)
frag_table(2)
frag_table(3)
