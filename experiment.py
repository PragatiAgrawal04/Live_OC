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


# get the last thursday of the current month
def last_thursday_version_2(year, month):
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

    return df_Expiry


# get the last thursday of the next month
def last_thursday(year, month):
    if month == 12:
        date = f"{year + 1}-01-01"
    if month == 1 or month == 2 or month == 3 or month == 4 or month == 5 or month == 6 or month == 7 or month == 8:
        date = f"{year}-0{month + 1}-01"
    if month == 9 or month == 10 or month == 11:
        date = f"{year}-{month + 1}-01"

    # we have a datetime series in our dataframe...
    df_Month = pd.to_datetime(date)

    # we can easily get the month's end date:
    df_mEnd = df_Month + pd.tseries.offsets.MonthEnd(1)

    # Thursday is weekday 3, so the offset for given weekday is
    offset = (df_mEnd.weekday() - 3) % 7

    # now to get the date of the last Thursday of the month, subtract it from
    # month end date:
    df_Expiry = df_mEnd - pd.to_timedelta(offset, unit='D')

    return df_Expiry



exchange = "NSE"


def current_market_price(ticker, exchange):
    url = f"https://www.google.com/finance/quote/{ticker}:{exchange}"

    for _ in range(1000000):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        class1 = "YMlKec fxKbKc"

        price = float(soup.find(class_=class1).text.strip()[1:].replace(",", ""))
        yield price

        time.sleep(5)


def get_dataframe(ticker):
    while True:
        try:

            url = f"https://www.nseindia.com/api/option-chain-equities?symbol={ticker}"
            headers = {"accept-encoding": "gzip, deflate, br, zstd",
                       "accept-language": "en-US,en;q=0.9",
                       "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", 
                       "cookie": '_ga=GA1.1.1104812566.1715673932; nsit=DXaQ2SbDGa9HsTXhwkNwpTo4; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTcxNjI4NzU3OSwiZXhwIjoxNzE2Mjk0Nzc5fQ.obJiODllMc8QHV25Ky95nMGFJ3bqgViUGSOVC1Hso5g; AKA_A2=A; _abck=AC0A6E579954CFC1BA4A76B56A1628F3~0~YAAQUGDQFwrjO5iPAQAAtSa2mguEKyWD8Exi2JMM7SIB2Vaynvo6hqa8bNg8MT8RY9CTsrBk784kyuiRTl22JTL34Xv0jQlwLyVLKPHnUrz4lbSwiTimmq1bMGiUQWw+Em11vzEBdw/G9nug37QlwBEaasEWcpHtnj3w9TWYMZ1eSw6dIlHIh448u9XdqXUuTjkawbtS2XqmlpQ1y6Plv4DpNWtMbPn1HuvQwwpKeHYou7NOryJWI6xpGiw26NrZSKpygwaEQhi40NbFzl3roBGs3ATgZI0k8jEnwtmWx2ZQIc/ca1DL2PYk2bL+sN70TYRaSF0cRtjVeCDp4Ll5rQtkpfNT+cAOhHQDT41OVocXWNzxDl1bEqnt/z+kNXekY/vUpLdSKPWJ4BeILPf1UQoKAU9mfcN3Nqs=~-1~-1~-1; bm_sz=D7A90F0BFCCC1F46AA3C2A0F601D2669~YAAQUGDQFw3jO5iPAQAAtSa2mhcWvmOKQLomwTNbF4/120ORyM8FDLEcEE/53z6N7+8iw/iMuZwLDBO7KdSIS4v0aB7/VT0uaLdAtpG/Jdh6J56lEFx7pPCO/E1ULJG3rRC14qLsvTiQG7CUG/fZJc7URZcxOkxKjysqIOZAAh5k1KqTb06VYOnHVsyxPCEC0B8tdxuoijb/Imna3lMwCyW17jA54t3DrRpQqfhdxpoA/ujP9fmnYK/EuOhXLpKBRr3Bm2EWWB265O8I4AE3mt9Tgl+7OsciLS52bthRQRkjgj5af2AKDvGuZuIIPehD3Hh/AD6EDjVdnCEly0Qts0l2ViJXFWj6Oyw8BunDAM7TzduFQ+4YgT4RVKslifzS5/m3INx6ylWCoXdrYa4=~3618101~4600901; defaultLang=en; ak_bmsc=4AF4263F444BE2EAB9A49B7DA87AF4CF~000000000000000000000000000000~YAAQUGDQF9TkO5iPAQAA0j62mhcGAPKGh03G8oc3BVV0Vt8xcN/DZ3BykjWCNLAOgjoCn6UD0t4/pbyJMozX+5oxHrj994irKPxyOStQO3uEEReh/oZv7ivp7tKHJdpBpDHC+UkdtrHWkeFOuq8MqXhT/JHaVCbBAxKvZ7+SYQlXl+o3luTRWQz29s+wT8NB4EYe35RB4Xiju5vYSXd7arNjkW7pYy/NBGATBsD7yNFdBWNpKU+zWBlAgKOXtFqVdxjsxNyCIRnlvPGda5WB5dXbqLyq6UeRubz7c2HfG5m3u2BKkcSxA9Ig0U5JwBeKTm+r+xlismoaRPSeFp5mLjx4CLLH0FpKbQLXAh8rYykggPPozxQ+PGiPSTlxgDTpiQxIgKTU85h9l8ZVsx83ak1REOtZAId/ihfZLakV2J5tRKJzuvRVJZ3PVIGn37+QVS9sZ8C8ZkP68n/8rlQT0A==; RT="z=1&dm=nseindia.com&si=a746dd1a-fbf2-473e-a100-db75208eb944&ss=lwg9b7lx&sl=0&se=8c&tt=0&bcn=%2F%2F17de4c19.akstat.io%2F&nu=kpaxjfo&cl=15198"; _ga_QJZ4447QD3=GS1.1.1716289493.19.0.1716289493.0.0.0; _ga_87M7PJ3R97=GS1.1.1716289494.22.0.1716289494.0.0.0; bm_sv=E7CFBC9E4C9334704757FF25BE39EACB~YAAQUGDQF+a/PpiPAQAAoV3TmhfPbn1UTpj3+aKLGPlxGB/VhxpbxpSUoBuci+xsLVvExEezWh//x5VP4+iZk1TjuMK2ySPH3nGpj26Ob4unZbR/Rc4Z6wTG2aJWuhDMb7VWjYQOUA/2Om2strUab/PGKml7nDgaIvtKMeNZSiRltXvs9JmxykxfPifKs+6Pu+5qG1dBZhpqvdUCU4Gs/I5RL/n6a4WFrurh6/ZE1UKLnpvkpC1z3VPvQGLHCuQ8+Vw=~1'
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

                # (last thursday (CE))
                today_year = datetime.datetime.now().year
                today_month = datetime.datetime.now().month
                today_day = datetime.datetime.now().day
                l_thursday = last_thursday_version_2(today_year, today_month)

                # if today is within the last thursday, then we will take current month last thursday as an adjusted_expiry
                if today_day < l_thursday.day or today_day == l_thursday.day and today_month == l_thursday.month:
                    adjusted_expiry = last_thursday_version_2(today_year, today_month)
                    print("in first if")
                # if today is greater than last thursday, then we will take next month last thursday as an adjusted_expiry
                if today_day > l_thursday.day and today_month == l_thursday.month:
                    adjusted_expiry = last_thursday(today_year, today_month)
                    print("in second if")

                format = '%d-%m-%Y'
                adjusted_expiry = adjusted_expiry.strftime(format)
                # year, month, day = str(l_thursday.date()).split("-")
                # l_thursday = f"{day}-{month}-{year}"
                # print(l_thursday)
                # print(l_thursday.date())
                # print(str(l_thursday.date()))
                # print(type(l_thursday.date()))
                # print(type(str(l_thursday.date())))

                # (last thursday (PE))
                today_year_pe = datetime.datetime.now().year
                today_month_pe = datetime.datetime.now().month
                today_day_pe = datetime.datetime.now().day
                l_thursday_pe = last_thursday_version_2(today_year_pe, today_month_pe)

                # if today is within the last thursday, then we will take current month last thursday as an adjusted_expiry
                if today_day_pe < l_thursday_pe.day or today_day_pe == l_thursday_pe.day and today_month_pe == l_thursday_pe.month:
                    adjusted_expiry_pe = last_thursday_version_2(today_year_pe, today_month_pe)
                    print("in first if")
                # if today is greater than last thursday, then we will take next month last thursday as an adjusted_expiry
                if today_day_pe > l_thursday_pe.day and today_month_pe == l_thursday_pe.month:
                    adjusted_expiry_pe = last_thursday(today_year_pe, today_month_pe)
                    print("in second if")

                format = '%d-%m-%Y'
                adjusted_expiry_pe = adjusted_expiry_pe.strftime(format)
                # year_pe, month_pe, day_pe = str(l_thursday_pe.date()).split("-")
                # l_thursday_pe = f"{day_pe}-{month_pe}-{year_pe}"

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

@st.experimental_fragment
def frag_table(table_number):
    shares = pd.read_csv("FNO Stocks - All FO Stocks List, Technical Analysis Scanner.csv")
    share_list = list(shares["Symbol"])
    selected_option = st.selectbox("Share List", share_list, key="share_list"+str(table_number))

    if selected_option in share_list:
        ticker = selected_option
        output_ce, output_pe = get_dataframe(ticker)
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
            #output_ce = output_ce.style.set_table_styles([{'backgroundColor': 'palegreen'}])
            st.dataframe(output_ce, column_config = {'strikePrice':'Strike Price',
                                                    'expiryDate':'Expiry Date',
                                                    'lastPrice':st.column_config.NumberColumn("Last Price",format="%.2f"),
                                                    'instrumentType':'Instrument'})
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
#*************************************************ONE******************************************************

#
# shares_1 = pd.read_csv("FNO Stocks - All FO Stocks List, Technical Analysis Scanner.csv")
# share_list_1 = list(shares_1["Symbol"])
# selected_option_1 = st.selectbox("Share List", share_list_1, key = "share_list_1")
#
# if selected_option_1 in share_list_1:
#     ticker_1 = selected_option_1
#     output_ce_1, output_pe_1 = get_dataframe(ticker_1)
#
#     ########################################## Stock LTP and Matrix #######################################
#     stock_ltp_1 = 0.0
#     for price in current_market_price(ticker_1, exchange):
#         stock_ltp_1 = price
#         break
#
#
#     # ********************************** MATRIX ******************************************
#     l1_1, l2_1 = len(output_ce_1), len(output_pe_1)
#     if l1_1 < l2_1:
#         fin_len_1 = l1_1
#     else:
#         fin_len_1 = l2_1
#     matrix_1 = np.zeros((fin_len_1, 4))
#     df_1 = pd.DataFrame(matrix_1, columns=["Call Ratio", "Call Effective Ratio", "Put Ratio", "Put Effective Ratio"])
#
#     for i in range(len(df_1)):
#         df_1.at[i, "Call Ratio"] = (output_ce_1["lastPrice"].iloc[i] / stock_ltp_1) * 100
#         df_1.at[i, "Call Effective Ratio"] = (((output_ce_1["strikePrice"].iloc[i] - stock_ltp_1) + output_ce_1["lastPrice"].iloc[i]) / stock_ltp_1) * 100
#         df_1.at[i, "Put Ratio"] = (output_pe_1["lastPrice"].iloc[i] / stock_ltp_1) * 100
#         df_1.at[i, "Put Effective Ratio"] = (((stock_ltp_1 - output_pe_1["strikePrice"].iloc[i]) + output_pe_1["lastPrice"].iloc[i]) / stock_ltp_1) * 100
#
#     # ************************************************************************************
#
#     col1_1, col2_1, col3_1 = st.columns(3)
#
#     with col1_1:
#         output_ce_1 = output_ce_1.style.set_properties(**{'background-color': 'palegreen'})
#         st.dataframe(output_ce_1)
#     with col2_1:
#         output_pe_1 = output_pe_1.style.set_properties(**{'background-color': 'antiquewhite'})
#         st.dataframe(output_pe_1)
#     with col3_1:
#         df_1 = df_1.style.set_properties(**{'background-color': 'paleturquoise'})
#         st.dataframe(df_1)
#
#     st.write(f'{ticker_1} LTP:', stock_ltp_1)
#
#
#
#
#
# #*************************************************TWO*********************************************
#
# shares_2 = pd.read_csv("FNO Stocks - All FO Stocks List, Technical Analysis Scanner.csv")
# share_list_2 = list(shares_2["Symbol"])
# selected_option_2 = st.selectbox("Share List", share_list_2, key = "share_list_2")
#
# if selected_option_2 in share_list_2:
#     ticker_2 = selected_option_2
#     output_ce_2, output_pe_2 = get_dataframe(ticker_2)
#
#     ########################################## Stock LTP and Matrix #######################################
#     stock_ltp_2 = 0.0
#     for price in current_market_price(ticker_2, exchange):
#         stock_ltp_2 = price
#         break
#
#
#     # ********************************** MATRIX ******************************************
#     l1_2, l2_2 = len(output_ce_2), len(output_pe_2)
#     if l1_2 < l2_2:
#         fin_len_2 = l1_2
#     else:
#         fin_len_2 = l2_2
#     matrix_2 = np.zeros((fin_len_2, 4))
#     df_2 = pd.DataFrame(matrix_2, columns=["Call Ratio", "Call Effective Ratio", "Put Ratio", "Put Effective Ratio"])
#
#     for i in range(len(df_2)):
#         df_2.at[i, "Call Ratio"] = (output_ce_2["lastPrice"].iloc[i] / stock_ltp_2) * 100
#         df_2.at[i, "Call Effective Ratio"] = (((output_ce_2["strikePrice"].iloc[i] - stock_ltp_2) + output_ce_2["lastPrice"].iloc[i]) / stock_ltp_2) * 100
#         df_2.at[i, "Put Ratio"] = (output_pe_2["lastPrice"].iloc[i] / stock_ltp_2) * 100
#         df_2.at[i, "Put Effective Ratio"] = (((stock_ltp_2 - output_pe_2["strikePrice"].iloc[i]) + output_pe_2["lastPrice"].iloc[i]) / stock_ltp_2) * 100
#
#     # ************************************************************************************
#     col1_2, col2_2, col3_2 = st.columns(3)
#
#     with col1_2:
#         output_ce_2 = output_ce_2.style.set_properties(**{'background-color': 'palegreen'})
#         st.dataframe(output_ce_2)
#     with col2_2:
#         output_pe_2 = output_pe_2.style.set_properties(**{'background-color': 'antiquewhite'})
#         st.dataframe(output_pe_2)
#     with col3_2:
#         df_2 = df_2.style.set_properties(**{'background-color': 'paleturquoise'})
#         st.dataframe(df_2)
#
#     st.write(f'{ticker_2} LTP:', stock_ltp_2)
#
